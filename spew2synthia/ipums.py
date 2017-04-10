import glob
import os

import aid
import conf
import spew


def translate(iso3):
    code = iso3
    pp_csvs = spew.find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    pp_csv = synth_file_name(code, 'people')
    (hh_ids, sc_ids, wp_ids) = out_pp_file(pp_csvs, spew.pp_mapper, pp_csv)
    aid.reorder(pp_csv, [17, 9, 3, 8, 12, 13, 14, 18, 7, 15, 15]) # TODO sp_work_id using sp_school_id


    ref_hh_ids = out_ref_hh_file(spew.find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix), spew.hh_mapper, os.devnull)  # out_file_name('ref_hh'))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name(code, 'households')
    out_hh_file(pp_csvs, spew.hh_mapper, hh_csv)
    # csv columns (input):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID
    # text columns (output):
    # sp_id,serialno,stcotrbg,hh_race,hh_income,hh_size,hh_age,latitude,longitude
    aid.reorder(hh_csv, [9, 3, 8, 14, 16, 4, 12, 11, 10])

    aid.touch_file(out_file_name(code, 'schools').replace('.csv', '.txt'))
    aid.touch_file(out_file_name(code, 'workplaces').replace('.csv', '.txt'))
    aid.touch_file(synth_file_name(code, 'gq').replace('.csv', '.txt'))
    aid.touch_file(synth_file_name(code, 'gq_people').replace('.csv', '.txt'))



def synth_file_name(code, type):
    return out_file_name(code, 'synth_' + type)


def out_file_name(code, name):
    out = '../populations'
    prefix = '/spew_1.2.0_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def out_pp_file(in_file_paths, mapper, out_file_path):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID+sporder
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 8
    RELP_COLUMN = 6
    SCHOOL_COLUMN = 14
    WORKPLACE_COLUMN = 0
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    skips = 0
    aid.mkdir(out_file_path)
    with open(out_file_path, 'w') as fout:
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        cells.append('sporder')
                    school_id = cells[SCHOOL_COLUMN]
                    sc_ids.add(school_id)
                    hid = cells[HID_COLUMN]
                    if cells[RELP_COLUMN] == '0':
                        hids.add(hid)
                    order = hid2cnt.get(hid, 0)
                    order += 1
                    cells.append(str(order))
                    hid2cnt[hid] = order
                    #workplace_id = cells[WORKPLACE_COLUMN]
                    #wp_ids.add(workplace_id)
                    row = ','.join([mapper(x) for x in cells])
                    fout.write(row + "\n")
    print('Skipped', skips, 'rows due to private schools')
    return hid2cnt.keys() | set(), sc_ids, wp_ids


def out_ref_hh_file(in_file_paths, mapper, out_file_path):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude, latitude
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 8
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
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 8
    aid.mkdir(out_file_path)
    hids = set()
    with open(out_file_path, 'w') as fout:
        file_count = 0
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count > 1:
                            continue
                    cells = line.split(',')
                    hid = cells[HID_COLUMN]
                    if hid not in hids or hid == 'SYNTHETIC_HID':
                        hids.add(hid)
                        mapped_cells = [mapper(x) for x in cells]
                        row = ','.join(mapped_cells)
                        fout.write(row)


def test():
    import filecmp
    translate('fji')
    actual = '../populations/spew_1.2.0_fji'
    expected = './expected/spew_1.2.0_fji'
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