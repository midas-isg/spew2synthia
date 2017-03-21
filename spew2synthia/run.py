import os
import subprocess

import conf


def main():
    # print(conf.path_puma_eco, os.listdir(conf.path_puma_eco))

    pp_csv = synth_file_name('people')
    (hh_ids, sc_ids, wp_ids) = out_pp_file(conf.file_pp, pp_mapper, pp_csv)
    reorder(pp_csv, [26, 8, 3, 7, 15, 14, 25, 29, 18, 27, 28])

    wp_csv = out_file_name('workplaces')
    out_wp_file(wp_csv, wp_ids)
    reorder(wp_csv, [4, 6, 2, 1])

    sc_csv = out_file_name('schools')
    out_sc_file(sc_csv, sc_ids)
    reorder(sc_csv, [3, 2, 5, 1, 1, 4, 1, 1, 1, 10, 1, 1, 1, 1, 7, 6, 1, 1])  # TODO missing variables used 1

    touch_file(synth_file_name('gq').replace('.csv', '.txt'))
    touch_file(synth_file_name('gq_people').replace('.csv', '.txt'))

    ref_hh_ids = out_ref_hh_file(conf.file_hh, hh_mapper, os.devnull)  # out_file_name('ref_hh'))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name('households')
    out_hh_file(conf.file_pp, hh_mapper, hh_csv)
    reorder(hh_csv, [8, 3, 7, 25, 5, 6, 15, 10, 9])


def touch_file(filename):
    open(filename, 'a').close()


def reorder(csv, columns):
    out_file_path = csv.replace('.csv', '.txt')
    print('reading', csv)
    print('writing', os.path.abspath(out_file_path))
    f = open(out_file_path, 'w')
    template = '","'.join(['$' + str(x) for x in columns])
    subprocess.run(["awk", 'BEGIN { FS = "," } { print ' + template + '}', csv], stdout=f)
    delete(csv)


def delete(file):
    print('deleting', file)
    os.remove(file)


def out_wp_file(out_file_path, wp_ids):
    import wp
    in_file_path = conf.path_env + '/workplaces.csv'
    print('reading', in_file_path)
    print('writing', os.path.abspath(out_file_path))
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


def out_sc_file(out_file_path, sc_ids):
    in_file_path = conf.path_env + '/public_schools.csv'
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


def to_private_school_ids():
    private_school_ids = set()
    with open(conf.path_env + '/private_schools.csv') as fin:
        for line in fin:
            cells = line.split(',')
            private_school_ids.add(cells[2][1:-1])
    return private_school_ids


def synth_file_name(type):
    return out_file_name('synth_' + type)


def out_file_name(name):
    out = '../populations'
    prefix = '/2010_ver1_' + conf.code
    return out + prefix + prefix + '_' + name + '.csv'


def out_pp_file(in_file_path, mapper, out_file_path):
    print('reading', in_file_path)
    print('writing', os.path.abspath(out_file_path))
    private_school_ids = to_private_school_ids()
    # print(len(private_school_ids), private_school_ids)
    HID_COLUMN = 7
    RELP_COLUMN = 17
    SCHOOL_COLUMN = 26
    WORKPLACE_COLUMN = 27
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    mkdir(out_file_path)
    skips = 0
    with open(in_file_path, 'r') as fin:
        with open(out_file_path, 'w') as fout:
            for line in fin:
                cells = line.rstrip('\n').split(',')
                if line.startswith('RT'):
                    cells.append('sporder')
                school_id = cells[SCHOOL_COLUMN]
                if school_id in private_school_ids:
                    # print('Skipped due to private school ID =', school_id, ':', line.rstrip('\n'))
                    skips += 1
                    continue
                else:
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


def out_ref_hh_file(in_file_path, mapper, out_file_path):
    print('reading', in_file_path)
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 7
    result = set()
    mkdir(out_file_path)
    with open(in_file_path, 'r') as fin:
        with open(out_file_path, 'w') as fout:
            for line in fin:
                cells = line.split(',')
                result.add(cells[HID_COLUMN])
                row = ','.join([mapper(x) for x in cells])
                fout.write(row)
    return result


def out_hh_file(in_file_path, mapper, out_file_path):
    print('reading', in_file_path)
    print('writing', os.path.abspath(out_file_path))
    RELP_COLUMN = 17
    mkdir(out_file_path)
    with open(in_file_path, 'r') as fin:
        with open(out_file_path, 'w') as fout:
            for line in fin:
                cells = line.split(',')
                relate = cells[RELP_COLUMN]
                if relate == '0' or relate == 'RELP':
                    mapped_cells = [mapper(x) for x in cells]
                    row = ','.join(mapped_cells)
                    fout.write(row)


def mkdir(out_file_path):
    dirname = os.path.dirname(out_file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def hh_mapper(x):
    return conf.hh_map.get(x, x)


def pp_mapper(x):
    return conf.pp_map.get(x, x)


def sc_mapper(x):
    return conf.sc_map.get(x, x)


def wp_mapper(x):
    return conf.wp_map.get(x, x)


main()
