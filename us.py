import os

import aid
import conf
import spew
import wp
_prefix2csvs = {}
_test_env_path = None


def translate(fips):
    env_path = _path_env(fips)
    pp_csvs = _find_csvs(conf.pp_prefix, fips)
    code = fips[:5]

    hh_ids, sc_ids, wp_ids = _translate_pp(pp_csvs, code)
    _translate_sc(env_path, sc_ids, code)
    _translate_wp(env_path, wp_ids, code)
    _cross_check_hids(fips, hh_ids)
    _translate_hh(pp_csvs, code)


def _translate_pp(pp_csvs, code):
    pp_csv = _output_csv_synth_file_path(code, 'people')
    gq_pp_csv = _output_csv_synth_file_path(code, 'gq_people')
    hh_ids, sc_ids, wp_ids = _save_pp_as_csv(pp_csvs, pp_csv, gq_pp_csv)
    _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv)
    return hh_ids, sc_ids, wp_ids


def _translate_sc(env_path, sc_ids, code):
    sc_csv = _output_csv_file_path(code, 'schools')
    _save_sc_as_csv(env_path, sc_csv, sc_ids)
    _save_sc_as_txt_with_reordering_columns(sc_csv)


def _translate_wp(env_path, wp_ids, code):
    wp_csv = _output_csv_file_path(code, 'workplaces')
    _save_wp_as_csv(env_path, wp_csv, wp_ids)
    _save_wp_as_txt_with_reordering_columns(wp_csv)


def _cross_check_hids(fips, hh_ids):
    ref_hh_ids = _to_household_ids(_find_csvs(conf.hh_prefix, fips))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        txt = 'Household IDs from people and household inputs are different:'
        raise Exception(txt, difference)


def _translate_hh(pp_csvs, code):
    hh_csv = _output_csv_synth_file_path(code, 'households')
    gq_csv = _output_csv_synth_file_path(code, 'gq')
    _save_hh_as_csv(pp_csvs, hh_csv, gq_csv)
    _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv)


def _save_pp_as_csv(in_file_paths, pp_path, gq_pp_path):
    type_column = 1
    hid_column = 7
    age_column = 14
    relp_column = 17
    school_column = 26
    workplace_column = 27
    columns = 29
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    aid.mkdir(pp_path)
    aid.mkdir(gq_pp_path)
    with open(pp_path, 'w') as pp_csv, open(gq_pp_path, 'w') as gq_pp_csv:
        print('writing', os.path.abspath(pp_path), os.path.abspath(gq_pp_path))
        csvs = [pp_csv, gq_pp_csv]
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for raw in fin:
                    line = raw.strip('\n')
                    is_header = line.startswith('RT')
                    if is_header:
                        file_count += 1
                        if file_count > 1:
                            continue
                        row = line + ',made-sporder'
                        for csv in csvs:
                            aid.write_and_check_columns(csv, row, columns)
                        continue
                    cells = line.split(',')
                    school_id = cells[school_column]
                    age = cells[age_column]
                    if school_id:
                        if int(age) > 19:
                            print('Skipped due to too old at age of', age,
                                  'to go to school ID =', school_id, ':', line)
                            continue
                    sc_ids.add(school_id)
                    hid = cells[hid_column]
                    if cells[relp_column] == '0':
                        hids.add(hid)
                    order = hid2cnt.get(hid, 0)
                    order += 1
                    hid2cnt[hid] = order
                    workplace_id = cells[workplace_column]
                    wp_ids.add(workplace_id)
                    csv = pp_csv if cells[type_column] == '1' else gq_pp_csv
                    row = line + ',' + str(order)
                    aid.write_and_check_columns(csv, row, columns)
    return hids, sc_ids, wp_ids


def _save_sc_as_csv(env_path, out_file_path, sc_ids):
    long_column = 5
    columns = 11
    in_file_paths = [env_path + '/public_schools.csv',
                     env_path + '/private_schools.csv']
    ids = set()
    with open(out_file_path, 'w') as fout:
        print('writing', os.path.abspath(out_file_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path) as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    sc_id = cells[2][1:-1]
                    if line.startswith('"","School"'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        row = ','.join(cells) + ',made-empty'
                        aid.write_and_check_columns(fout, row, columns)
                    elif sc_id in sc_ids:
                        cells.append('')
                        row = ','.join(cells[:long_column])
                        if len(cells) < columns:
                            row += ',,'
                        row += ',' + ','.join(cells[long_column:])
                        aid.write_and_check_columns(fout, row, columns)
                    ids.add(sc_id)
    difference = sc_ids.difference(ids)
    difference.discard('')
    difference.discard('school_id')
    if difference:
        raise Exception(str(difference) + " are not found!")
    return ids


def _save_wp_as_csv(env_path, out_file_path, wp_ids):
    in_file_path = env_path + '/workplaces.csv'
    ids = set()
    columns = 8
    with open(out_file_path, 'w') as fout:
        print('writing', os.path.abspath(out_file_path))
        with open(in_file_path) as fin:
            print('reading', in_file_path)
            for raw in fin:
                line = raw.strip('\n')
                cells = line.split(',')
                wkb_hex = str(cells[5][1:-1])
                wp_id = cells[1]
                if wkb_hex == 'wkb_geometry':
                    row = 'made-longitude,made-latitude,' + line
                    aid.write_and_check_columns(fout, row, columns)
                elif wp_id in wp_ids:
                    row = wp.to_long_lat_from_hex(wkb_hex) + ',' + line
                    aid.write_and_check_columns(fout, row, columns)
                ids.add(wp_id)
    difference = wp_ids.difference(ids)
    difference.discard('')
    difference.discard('workplace_id')
    if difference:
        raise Exception(difference, "are not found!")


def _to_household_ids(in_file_paths):
    hid_column = 7
    result = set()
    for in_file_path in in_file_paths:
        print('reading', in_file_path)
        with open(in_file_path, 'r') as fin:
            for line in fin:
                cells = line.split(',')
                if len(cells) <= hid_column:
                    print(line)
                result.add(cells[hid_column])
    return result


def _save_hh_as_csv(in_file_paths, hh_path, gq_path):
    type_column = 1
    relp_column = 17
    columns = 29
    aid.mkdir(hh_path)
    aid.mkdir(gq_path)
    with open(hh_path, 'w') as hh_csv, open(gq_path, 'w') as gq_csv:
        print('writing', os.path.abspath(hh_path), os.path.abspath(gq_path))
        file_count = 0
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for raw in fin:
                    line = raw.strip('\n')
                    cells = line.split(',')
                    relate = cells[relp_column]
                    is_header = relate == 'RELP'
                    if is_header:
                        file_count += 1
                        if file_count == 1:
                            row = line + ',made-gq_type'
                            aid.write_and_check_columns(hh_csv, row, columns)
                            aid.write_and_check_columns(gq_csv, row, columns)
                        continue
                    if relate == '0':
                        row = line + ','
                        csv = hh_csv if cells[type_column] == '1' else gq_csv
                        aid.write_and_check_columns(csv, row, columns)


def _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv):
    # csv columns (input):
    #  0 RT,TYPE,SERIALNO,puma_id,HINCP,
    #  5 NP,place_id,SYNTHETIC_HID,longitude,latitude,
    # 10 RT,puma_id,ST,SEX,AGEP,
    # 15 SCH,SCHG,RELP,HISP,ESR,
    # 20 PINCP,NATIVITY,OCCP,POBP,RAC1P,
    # 25 SYNTHETIC_PID,school_id,workplace_id+made-sporder
    # text columns (output):
    # sp_id,sp_hh_id,serialno,stcotrbg,age,
    # sex,race,sporder,relate,sp_school_id,
    # sp_work_id
    pp_columns = [26, 8, 3, 7, 15, 14, 25, 29, 18, 27, 28]
    aid.reorder_and_check_header(pp_csv, pp_columns, 'synth_people.txt-us')
    # text columns (output):
    # sp_id,sp_gq_id,sporder,age,sex
    gp_columns = [26, 8, 29, 15, 14]
    aid.reorder_and_check_header(gq_pp_csv, gp_columns,
                                 'synth_gq_people.txt-us')


def _save_sc_as_txt_with_reordering_columns(sc_csv):
    # csv columns (input):
    #  0 "","School","ID","CoNo","StNo",
    #  5 "Long","Lat","Low","High","Students",
    # 10 made-empty
    # text columns (output):
    # sp_id,name,stabbr,address,city,
    # county,zipcode,zip4,nces_id,total,
    # prek,kinder,gr01_gr1
    sc_columns = [3, 2, 5, 11, 11,
                  4, 11, 11, 11, 10,
                  11, 11, 11, 11, 7,
                  6, 11, 11]
    aid.reorder_and_check_header(sc_csv, sc_columns, 'schools.txt-us')


def _save_wp_as_txt_with_reordering_columns(wp_csv):
    # csv columns (input):
    # 0 longitude,latitude,"","workplace_id","stcotr",
    # 5 "employees","placed","wkb_geometry"
    # text columns (output):
    # sp_id,workers,latitude,longitude
    aid.reorder_and_check_header(wp_csv, [4, 6, 2, 1], 'workplaces.txt-us')


def _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv):
    # csv columns (input):
    #  0 RT,TYPE,SERIALNO,puma_id,HINCP,
    #  5 NP,place_id,SYNTHETIC_HID,longitude,latitude,
    # 10 RT,puma_id,ST,SEX,AGEP,
    # 15 SCH,SCHG,RELP,HISP,ESR,
    # 20 PINCP,NATIVITY,OCCP,POBP,RAC1P,
    # 25 SYNTHETIC_PID,school_id,workplace_id,made-gq_type
    # text columns (output):
    # sp_id,serialno,stcotrbg,hh_race,hh_income,
    # hh_size,hh_age,latitude,longitude
    hh_columns = [8, 3, 7, 25, 5, 6, 15, 10, 9]
    aid.reorder_and_check_header(hh_csv, hh_columns, 'synth_households.txt-us')
    # text columns (output):
    # sp_id,gq_type,persons,stcotrbg,latitude,longitude
    gq_columns = [8, 29, 6, 7, 10, 9]
    aid.reorder_and_check_header(gq_csv, gq_columns, 'synth_gq.txt-us')


def _output_csv_synth_file_path(code, type):
    return _output_csv_file_path(code, 'synth_' + type)


def _output_csv_file_path(code, name):
    out = 'populations'
    prefix = '/2010_ver1_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def _find_csvs(prefix, fips):
    result = _prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs(prefix, fips)


def _path_env(fips):
    if _test_env_path:
        return _test_env_path
    return conf.pattern_env.format(state=fips[:2])


def test():
    import filecmp
    path_us = 'spew_sample/usa'
    _prefix2csvs[conf.hh_prefix] = [path_us + '/household_01077010100.csv',
                                    path_us + '/hh_header.csv']
    _prefix2csvs[conf.pp_prefix] = [path_us + '/people_01077010100.csv',
                                    path_us + '/pp_header.csv']
    global _test_env_path
    _test_env_path = path_us + '/env'
    translate('01077010100')
    actual = './populations/2010_ver1_01077'
    expected = './expected/2010_ver1_01077'
    dcmp = filecmp.dircmp(actual, expected)
    _same_files(dcmp)
    if dcmp.diff_files:
        raise Exception('Difference: ' + str(dcmp.diff_files))


def _same_files(dcmp):
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