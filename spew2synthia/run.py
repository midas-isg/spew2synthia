import os
import subprocess

import aid
import conf
import spew


def main(fips):
    print(conf.path_usa, os.listdir(conf.path_usa))
    code = fips[:5]
    pp_csvs = spew.find_csvs(conf.pp_prefix, fips)
    env_path = path_env(fips)

    pp_csv = synth_file_name(code, 'people')
    (hh_ids, sc_ids, wp_ids) = out_pp_file(env_path, pp_csvs, pp_mapper, pp_csv)
    reorder(pp_csv, [26, 8, 3, 7, 15, 14, 25, 29, 18, 27, 28])

    sc_csv = out_file_name(code, 'schools')
    out_sc_file(env_path, sc_csv, sc_ids)
    reorder(sc_csv, [3, 2, 5, 1, 1, 4, 1, 1, 1, 10, 1, 1, 1, 1, 7, 6, 1, 1])  # missing variables used 1

    wp_csv = out_file_name(code, 'workplaces')
    out_wp_file(env_path, wp_csv, wp_ids)
    reorder(wp_csv, [4, 6, 2, 1])

    ref_hh_ids = out_ref_hh_file(spew.find_csvs(conf.hh_prefix, fips), hh_mapper, os.devnull)  # out_file_name('ref_hh'))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name(code, 'households')
    out_hh_file(pp_csvs, hh_mapper, hh_csv)
    reorder(hh_csv, [8, 3, 7, 25, 5, 6, 15, 10, 9])

    touch_file(synth_file_name(code, 'gq').replace('.csv', '.txt'))
    touch_file(synth_file_name(code, 'gq_people').replace('.csv', '.txt'))


def touch_file(filename):
    open(filename, 'a').close()


def reorder(csv, columns):
    out_file_path = csv.replace('.csv', '.txt')
    print('writing', os.path.abspath(out_file_path))
    print('reading', csv)
    f = open(out_file_path, 'w')
    template = '","'.join(['$' + str(x) for x in columns])
    subprocess.run(["awk", 'BEGIN { FS = "," } { print ' + template + '}', csv], stdout=f)
    delete(csv)


def delete(file):
    print('deleting', file)
    os.remove(file)


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
                    row = ','.join([wp_mapper(x) for x in cells])
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
    in_file_path = env_path + '/public_schools.csv'
    print('reading', in_file_path)
    print('writing', os.path.abspath(out_file_path))
    ids = set()
    with open(in_file_path) as fin:
        with open(out_file_path, 'w') as fout:
            for line in fin:
                cells = line.rstrip('\n').split(',')
                id = cells[2][1:-1]
                if line.startswith('"","School"'):
                    row = ','.join([sc_mapper(x) for x in cells])
                    fout.write(row + '\n')
                elif id in sc_ids:
                    fout.write(line)
                ids.add(id)
    difference = sc_ids.difference(ids)
    difference.discard('')
    difference.discard('school_id')
    if difference:
        raise Exception(str(difference) + " are not found!")
    return ids


def to_private_school_ids(env_path):
    private_school_ids = set()
    with open(env_path + '/private_schools.csv') as fin:
        for line in fin:
            cells = line.split(',')
            private_school_ids.add(cells[2][1:-1])
    return private_school_ids


def path_env(fips):
    return conf.pattern_env.format(state=fips[:2])


def synth_file_name(code, type):
    return out_file_name(code, 'synth_' + type)


def out_file_name(code, name):
    out = '../populations'
    prefix = '/2010_ver1_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def out_pp_file(env_path, in_file_paths, mapper, out_file_path):
    print('writing', os.path.abspath(out_file_path))
    private_school_ids = to_private_school_ids(env_path)
    # print(len(private_school_ids), private_school_ids)
    HID_COLUMN = 7
    RELP_COLUMN = 17
    SCHOOL_COLUMN = 26
    WORKPLACE_COLUMN = 27
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    skips = 0
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    if line.startswith('RT'):
                        cells.append('sporder')
                    school_id = cells[SCHOOL_COLUMN]
                    age = cells[RELP_COLUMN - 3]
                    if school_id in private_school_ids:
                        # print('Skipped due to private school ID =', school_id, ':', line.rstrip('\n'))
                        skips += 1
                        continue
                    elif school_id and age != 'AGEP':
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
                    row = ','.join([mapper(x) for x in cells])
                    fout.write(row + "\n")
    print('Skipped', skips, 'rows due to private schools')
    return hid2cnt.keys() | set(), sc_ids, wp_ids


def out_ref_hh_file(in_file_paths, mapper, out_file_path):
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 7
    result = set()
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    cells = line.split(',')
                    if len(cells) <= HID_COLUMN:
                        print(line)
                    result.add(cells[HID_COLUMN])
                    row = ','.join([mapper(x) for x in cells])
                    fout.write(row)
    return result


def out_hh_file(in_file_paths, mapper, out_file_path):
    print('writing', os.path.abspath(out_file_path))
    RELP_COLUMN = 17
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    cells = line.split(',')
                    relate = cells[RELP_COLUMN]
                    if relate == '0' or relate == 'RELP':
                        mapped_cells = [mapper(x) for x in cells]
                        row = ','.join(mapped_cells)
                        fout.write(row)


def hh_mapper(x):
    return conf.hh_map.get(x, x)


def pp_mapper(x):
    return conf.pp_map.get(x, x)


def sc_mapper(x):
    return conf.sc_map.get(x, x)


def wp_mapper(x):
    return conf.wp_map.get(x, x)


def test():
    import filecmp
    main('01077010100')
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


# test()
