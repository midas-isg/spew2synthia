import os

import aid
import conf
import spew

prefix2csvs = {}
reversed_sex = {'1': '2', '2': '1'}
max_age = 99
age_group2age = {
    '1': aid.str_cycle(range(0, 5)),
    '2': aid.str_cycle(range(5, 7)),
    '3': aid.str_cycle(range(7, 10)),
    '4': aid.str_cycle(range(10, 12)),
    '5': aid.str_cycle(range(12, 15)),
    '6': aid.str_cycle(range(15, 18)),
    '7': aid.str_cycle(range(18, 20)),
    '8': aid.str_cycle(range(20, 25)),
    '9': aid.str_cycle(range(25, 30)),
    '10': aid.str_cycle(range(30, 35)),
    '11': aid.str_cycle(range(35, 40)),
    '12': aid.str_cycle(range(40, 45)),
    '13': aid.str_cycle(range(45, 50)),
    '14': aid.str_cycle(range(50, 55)),
    '15': aid.str_cycle(range(55, 60)),
    '16': aid.str_cycle(range(60, 65)),
    '17': aid.str_cycle(range(65, 70)),
    '18': aid.str_cycle(range(70, 75)),
    '19': aid.str_cycle(range(75, 80)),
    '20': aid.str_cycle(range(80, 85)),
    '21': aid.str_cycle(range(85, max_age)),
    '88': aid.str_cycle([max_age])
}


def translate(iso3):
    code = iso3
    pp_csvs = find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    hh_ids = translate_pp(pp_csvs, code)
    cross_check_hids(iso3, hh_ids)
    translate_hh(pp_csvs, code)
    aid.touch_require_file(code, 'schools')
    aid.touch_require_file(code, 'workplaces')
    aid.touch_file(aid.output_csv_synth_file_path(code, 'gq').replace('.csv', '.txt'))
    aid.touch_file(aid.output_csv_synth_file_path(code, 'gq_people').replace('.csv', '.txt'))


def translate_pp(pp_csvs, code):
    pp_csv = aid.output_csv_synth_file_path(code, 'people')
    hh_ids = out_pp_file(pp_csvs, pp_csv)
    save_pp_as_txt_with_reordering_columns(pp_csv)
    return hh_ids


def cross_check_hids(iso3, hh_ids):
    hh_csvs = find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix)
    ref_hh_ids = to_household_ids(hh_csvs)
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        msg = 'Household IDs from people and household inputs are different:'
        raise Exception(msg, difference)


def translate_hh(pp_csvs, code):
    hh_csv = aid.output_csv_synth_file_path(code, 'households')
    out_hh_file(pp_csvs, hh_csv)
    save_hh_as_txt_with_reordering_columns(hh_csv)


def out_pp_file(in_file_paths, pp_path):
    """  0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID """
    hid_column = 3
    sex_column = 14
    agegrp_column = 6
    more_headers = 'made-sporder,made-empty,made-sex,made-age'
    columns = 20
    hid2cnt = {}
    aid.mkdir(pp_path)
    with open(pp_path, 'w') as pp_csv:
        print('writing', os.path.abspath(pp_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for raw in fin:
                    line = raw.rstrip('\n')
                    if line.startswith('SERIALNO'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        row = line + ',' + more_headers
                        aid.write_and_check_columns(pp_csv, row, columns)
                    else:
                        cells = line.split(',')
                        sex = cells[sex_column]
                        agegroup = cells[agegrp_column]
                        hid = cells[hid_column]
                        order = hid2cnt.get(hid, 0) + 1
                        hid2cnt[hid] = order
                        row = line + ',' + ','.join([
                            str(order),
                            '',
                            reversed_sex.get(sex, sex),
                            to_age(agegroup)
                        ])
                        aid.write_and_check_columns(pp_csv, row, columns)
    return hid2cnt.keys() | set()


def to_household_ids(in_file_paths):
    """ SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude, latitude """
    hid_column = 3
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


def out_hh_file(in_file_paths, hh_path):
    """  0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID """
    hid_column = 3
    more_header = 'made-empty'
    columns = 17
    aid.mkdir(hh_path)
    with open(hh_path, 'w') as hh_csv:
        print('writing', os.path.abspath(hh_path))
        file_count = 0
        hids = set()
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for raw in fin:
                    line = raw.strip('\n')
                    if line.startswith('SERIALNO'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        row = line + ',' + more_header
                        aid.write_and_check_columns(hh_csv, row, columns)
                    else:
                        cells = line.split(',')
                        hid = cells[hid_column]
                        if hid not in hids:
                            hids.add(hid)
                            row = line + ','
                            aid.write_and_check_columns(hh_csv, row, columns)


def save_pp_as_txt_with_reordering_columns(pp_csv):
    """ csv columns (input):
         0 serialno,puma_id,stcotrbg,sp_hh_id,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,sex,
        15 sp_id,made-sporder,made-empty,made-sex,made-age
        text columns (output):
        sp_id,sp_hh_id,serialno,stcotrbg,age,
        sex,race,sporder,relate,sp_school_id,
        sp_work_id """
    pp_columns = [16, 4, 1, 3, 20, 19, 18, 17, 18, 18, 18]
    aid.reorder_and_check_header(pp_csv, pp_columns, 'synth_people.txt-ca')


def save_hh_as_txt_with_reordering_columns(hh_csv):
    """ csv columns (input):
        serialno,puma_id,stcotrbg,sp_id,longitude,
        latitude,AGEGRP,HRSWRK,IMMSTAT,hh_income,
        MODE,OCC,POB,RELIGION,SEX,
        SYNTHETIC_PID,made-empty,sex
        text columns (output):
        sp_id,serialno,stcotrbg,hh_race,hh_income,
        hh_size,hh_age,latitude,longitude """
    hh_columns = [4, 1, 3, 17, 10, 17, 17, 6, 5]
    aid.reorder_and_check_header(hh_csv, hh_columns, 'synth_households.txt-ca')


def to_age(agegroup):
    iterable = age_group2age.get(agegroup, None)
    return next(iterable) if iterable else agegroup


def find_csvs_by_iso3_and_prefix(iso3, prefix):
    result = prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs_by_iso3_and_prefix(iso3, prefix)


def test():
    prefix2csvs[conf.hh_prefix] = ['spew_sample/can/household_4620440.00.csv']
    prefix2csvs[conf.pp_prefix] = ['spew_sample/can/people_4620440.00.csv']
    import filecmp
    translate('can')
    actual = './populations/spew_1.2.0_can'
    expected = './expected/spew_1.2.0_can'
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
