import os

import aid
import conf
import spew
prefix2csvs = {}
test_env_path = None


def translate(fips):
    code = fips[:5]
    pp_csvs = find_csvs(conf.pp_prefix, fips)
    env_path = path_env(fips)

    pp_csv = synth_file_name(code, 'people')
    (hh_ids, sc_ids, wp_ids) = out_pp_file(env_path, pp_csvs, spew.pp_mapper, pp_csv)
    # csv columns (input):
    # RT,TYPE,SERIALNO,puma_id,HINCP, NP,place_id,SYNTHETIC_HID,longitude,latitude,
    # RT,puma_id,ST,SEX,AGEP, SCH,SCHG,RELP,HISP,ESR,
    # PINCP,NATIVITY,OCCP,POBP,RAC1P, SYNTHETIC_PID,school_id,workplace_id+sporder
    # text columns (output):
    # sp_id,sp_hh_id,serialno,stcotrbg,age,sex,race,sporder,relate,sp_school_id,sp_work_id
    aid.reorder(pp_csv, [26, 8, 3, 7, 15, 14, 25, 29, 18, 27, 28])

    sc_csv = out_file_name(code, 'schools')
    out_sc_file(env_path, sc_csv, sc_ids)
    # csv columns (input):
    # "","School","ID","CoNo","StNo", "Long","Lat","Low","High","Students"
    # text columns (output):
    # sp_id,name,stabbr,"","",county,"","","",total,"","","","",latitude,longitude,"",""
    aid.reorder(sc_csv, [3, 2, 5, 1, 1, 4, 1, 1, 1, 10, 1, 1, 1, 1, 7, 6, 1, 1])  # missing variables used 1

    wp_csv = out_file_name(code, 'workplaces')
    out_wp_file(env_path, wp_csv, wp_ids)
    # csv columns (input):
    # longitude,latitude,"","workplace_id","stcotr", "employees","placed","wkb_geometry"
    # text columns (output):
    # sp_id,workers,latitude,longitude
    aid.reorder(wp_csv, [4, 6, 2, 1])

    ref_hh_ids = out_ref_hh_file(find_csvs(conf.hh_prefix, fips), spew.hh_mapper, os.devnull)
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name(code, 'households')
    out_hh_file(pp_csvs, spew.hh_mapper, hh_csv)
    # csv columns (input):
    # RT,TYPE,SERIALNO,puma_id,HINCP, NP,place_id,SYNTHETIC_HID,longitude,latitude,
    # RT,puma_id,ST,SEX,AGEP, SCH,SCHG,RELP,HISP,ESR,
    # PINCP,NATIVITY,OCCP,POBP,RAC1P, SYNTHETIC_PID,school_id,workplace_id
    # text columns (output):
    # sp_id,serialno,stcotrbg,hh_race,hh_income,hh_size,hh_age,latitude,longitude
    aid.reorder(hh_csv, [8, 3, 7, 25, 5, 6, 15, 10, 9])

    aid.touch_file(synth_file_name(code, 'gq').replace('.csv', '.txt'))
    aid.touch_file(synth_file_name(code, 'gq_people').replace('.csv', '.txt'))


def find_csvs(prefix, fips):
    result = prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs(prefix, fips)


def out_wp_file(env_path, out_file_path, wp_ids):
    import wp
    in_file_path = env_path + '/workplaces.csv'
    print('writing', os.path.abspath(out_file_path))
    print('reading', in_file_path)
    ids = set()
    with open(in_file_path) as fin:
        with open(out_file_path, 'w') as fout:
            for line in fin:
                cells = line.split(',')
                wkb_hex = str(cells[5][1:-2])
                id = cells[1]
                if wkb_hex == 'wkb_geometry':
                    row = ','.join(spew.wp_mapper(x) for x in cells)
                    fout.write('longitude,latitude,' + row)
                elif id in wp_ids:
                    fout.write(wp.to_long_lat_from_hex(wkb_hex) + ',' + line)
                ids.add(id)
    difference = wp_ids.difference(ids)
    difference.discard('')
    difference.discard('workplace_id')
    if difference:
        raise Exception(str(difference) + " are not found!")


def out_sc_file(env_path, out_file_path, sc_ids):
    LONG_COLUMN = 5
    COLUMNS = 10
    in_file_paths = [env_path + '/public_schools.csv', env_path + '/private_schools.csv']
    ids = set()
    with open(out_file_path, 'w') as fout:
        print('writing', os.path.abspath(out_file_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path) as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    id = cells[2][1:-1]
                    if line.startswith('"","School"'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        row = ','.join(spew.sc_mapper(x) for x in cells)
                        fout.write(row + '\n')
                    elif id in sc_ids:
                        row = ','.join(x for x in cells[:LONG_COLUMN])
                        if len(cells) < COLUMNS:
                            row += ',,'
                        row += ',' + ','.join(x for x in cells[LONG_COLUMN:])
                        fout.write(row + '\n')
                    ids.add(id)
    difference = sc_ids.difference(ids)
    difference.discard('')
    difference.discard('school_id')
    if difference:
        raise Exception(str(difference) + " are not found!")
    return ids


def path_env(fips):
    if test_env_path:
        return test_env_path
    return conf.pattern_env.format(state=fips[:2])


def synth_file_name(code, type):
    return out_file_name(code, 'synth_' + type)


def out_file_name(code, name):
    out = '../populations'
    prefix = '/2010_ver1_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def out_pp_file(env_path, in_file_paths, mapper, out_file_path):
    HID_COLUMN = 7
    RELP_COLUMN = 17
    SCHOOL_COLUMN = 26
    WORKPLACE_COLUMN = 27
    AGE_COLUMN = 14
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        file_count = 0
        print('writing', os.path.abspath(out_file_path))
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    if line.startswith('RT'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        cells.append('sporder')
                    school_id = cells[SCHOOL_COLUMN]
                    age = cells[AGE_COLUMN]
                    if school_id and age != 'AGEP':
                        if int(age) > 19:
                            print('Skipped due to too old at age of ' + age + ' to go to school ID =', school_id, ':', line.rstrip('\n'))
                            continue
                    sc_ids.add(school_id)
                    hid = cells[HID_COLUMN]
                    if cells[RELP_COLUMN] == '0':
                        hids.add(hid)
                    order = hid2cnt.get(hid, 0)
                    order += 1
                    cells.append(str(order))
                    hid2cnt[hid] = order
                    workplace_id = cells[WORKPLACE_COLUMN]
                    wp_ids.add(workplace_id)
                    row = ','.join(mapper(x) for x in cells)
                    fout.write(row + "\n")
    return hid2cnt.keys() | set(), sc_ids, wp_ids


def out_ref_hh_file(in_file_paths, mapper, out_file_path):
    HID_COLUMN = 7
    result = set()
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        print('writing', os.path.abspath(out_file_path))
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    cells = line.split(',')
                    if len(cells) <= HID_COLUMN:
                        print(line)
                    result.add(cells[HID_COLUMN])
                    row = ','.join(mapper(x) for x in cells)
                    fout.write(row)
    return result


def out_hh_file(in_file_paths, mapper, out_file_path):
    RELP_COLUMN = 17
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        print('writing', os.path.abspath(out_file_path))
        file_count = 0
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    cells = line.split(',')
                    relate = cells[RELP_COLUMN]
                    if relate == 'RELP':
                        file_count += 1
                        if file_count > 1:
                            continue
                    if relate == '0' or relate == 'RELP':
                        mapped_cells = (mapper(x) for x in cells)
                        row = ','.join(mapped_cells)
                        fout.write(row)


def test():
    import filecmp
    path_us = 'spew_sample/usa'
    prefix2csvs[conf.hh_prefix] = [path_us + '/household_01077010100.csv', path_us + '/hh_header.csv']
    prefix2csvs[conf.pp_prefix] = [path_us + '/people_01077010100.csv', path_us + '/pp_header.csv']
    global test_env_path
    test_env_path = path_us + '/env'
    translate('01077010100')
    actual = '../populations/2010_ver1_01077'
    expected = './expected/2010_ver1_01077'
    dcmp = filecmp.dircmp(actual, expected)
    same_files(dcmp)
    if dcmp.diff_files:
        raise Exception('Difference: ' + str(dcmp.diff_files))


def same_files(dcmp):
    actual_files = set(dcmp.left_list)
    expected_files = set(dcmp.right_list)
    extras = actual_files.difference(expected_files)
    if extras:
        raise Exception('Extra files: ' + str(extras))
    missing = expected_files.difference(actual_files)
    if missing:
        raise Exception('Missing files: ' + str(missing))


if __name__ == "__main__":
    test()