import os

import aid
import conf
import spew

_prefix2csvs = {}
_reversed_sex = {'1': '2', '2': '1'}
_max_age = 88
_age_group2age = {
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
    '21': aid.str_cycle(range(85, _max_age)),
    '88': aid.str_cycle([_max_age])
}


def translate(iso3):
    code = iso3
    pp_csvs = _find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    hid2cnt = _translate_pp(pp_csvs, code)
    _cross_check_hids(iso3, hid2cnt.keys() | set())
    _translate_hh(pp_csvs, hid2cnt, code)
    aid.touch_require_file(code, 'schools')
    aid.touch_require_file(code, 'workplaces')


def _translate_pp(pp_csvs, code):
    pp_csv = aid.output_csv_synth_file_path(code, 'people')
    gq_pp_csv = aid.output_csv_synth_file_path(code, 'gq_people')
    hid2cnt = _save_pp_as_csv(pp_csvs, pp_csv, gq_pp_csv)
    _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv)
    return hid2cnt


def _cross_check_hids(iso3, hh_ids):
    hh_csvs = _find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix)
    ref_hh_ids = _to_household_ids(hh_csvs)
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        msg = 'Household IDs from people and household inputs are different:'
        raise Exception(msg, difference)


def _translate_hh(pp_csvs, hid2cnt, code):
    hh_csv = aid.output_csv_synth_file_path(code, 'households')
    gq_csv = aid.output_csv_synth_file_path(code, 'gq')
    _save_hh_as_csv(pp_csvs, hid2cnt, hh_csv, gq_csv)
    _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv)


def _save_pp_as_csv(in_file_paths, pp_path, gq_pp_path):
    """  0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID """
    hid_column = 3
    agegrp_column = 6
    sex_column = 14
    more_headers = 'made-sporder,made-empty,made-sex,made-age'
    columns = 20
    hid2cnt = {}
    aid.mkdir(pp_path)
    aid.mkdir(gq_pp_path)
    with open(pp_path, 'w') as pp_csv, open(gq_pp_path, 'w') as gq_pp_csv:
        print('writing', os.path.abspath(pp_path), os.path.abspath(gq_pp_path))
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
                        aid.write_and_check_columns(gq_pp_csv, row, columns)
                    else:
                        cells = line.split(',')
                        sex = cells[sex_column]
                        agegroup = cells[agegrp_column]
                        hid = cells[hid_column]
                        order = hid2cnt.get(hid, 0) + 1
                        hid2cnt[hid] = order
                        row = ','.join([
                            line,
                            str(order),
                            '',
                            _reversed_sex.get(sex, sex),
                            _to_age(agegroup)
                        ])
                        aid.write_and_check_columns(pp_csv, row, columns)
    return hid2cnt


def _to_household_ids(in_file_paths):
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


def _save_hh_as_csv(in_file_paths, hid2cnt, hh_path, gq_path):
    """  0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID """
    hid_column = 3
    more_header = 'made-empty,made-persons'
    columns = 18
    aid.mkdir(hh_path)
    with open(hh_path, 'w') as hh_csv, open(gq_path, 'w') as gq_csv:
        print('writing', os.path.abspath(hh_path), os.path.abspath(gq_path))
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
                        aid.write_and_check_columns(gq_csv, row, columns)
                    else:
                        cells = line.split(',')
                        hid = cells[hid_column]
                        if hid not in hids:
                            hids.add(hid)
                            row = line + ',' + ',' + str(hid2cnt[hid])
                            aid.write_and_check_columns(hh_csv, row, columns)


def _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv):
    """ csv columns (input):
          0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID,made-sporder,made-empty,made-sex,made-age
        text columns (output):
        sp_id,sp_hh_id,serialno,stcotrbg,age,
        sex,race,sporder,relate,sp_school_id,
        sp_work_id """
    pp_columns = [16, 4, 1, 3, 20,
                  19, 18, 17, 18, 18,
                  18]
    aid.reorder_and_check_header(pp_csv, pp_columns, 'synth_people.txt-ca')
    # text columns (output):
    # sp_id,sp_gq_id,sporder,age,sex
    gq_pp_columns = [16, 4, 17, 20, 19]
    aid.reorder_and_check_header(gq_pp_csv, gq_pp_columns,
                                 'synth_gq_people.txt-ca')


def _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv):
    """ csv columns (input):

         0 SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude,
         5 latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
        10 MODE,OCC,POB,RELIGION,SEX,
        15 SYNTHETIC_PID,made-empty,made-persons
        text columns (output):
        sp_id,serialno,stcotrbg,hh_race,hh_income,
        hh_size,hh_age,latitude,longitude """
    hh_columns = [4, 1, 3, 17, 17,
                  18, 17, 6, 5]
    aid.reorder_and_check_header(hh_csv, hh_columns, 'synth_households.txt-ca')
    # text columns (output):
    # sp_id,gq_type,persons,stcotrbg,
    # latitude,longitude
    gq_columns = [4, 17, 17, 3,
                  6, 5]
    aid.reorder_and_check_header(gq_csv, gq_columns, 'synth_gq.txt-ca')


def _to_age(agegroup):
    iterable = _age_group2age.get(agegroup, None)
    return next(iterable) if iterable else agegroup


def _find_csvs_by_iso3_and_prefix(iso3, prefix):
    result = _prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs_by_iso3_and_prefix(iso3, prefix)


def test():
    _prefix2csvs[conf.hh_prefix] = ['spew_sample/can/household_4620440.00.csv']
    _prefix2csvs[conf.pp_prefix] = ['spew_sample/can/people_4620440.00.csv']
    import filecmp
    translate('can')
    actual = './populations/spew_1.2.0_can'
    expected = './expected/spew_1.2.0_can'
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
