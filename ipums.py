import os
import sys

import aid
import conf
import spew
prefix2csvs = {}
age2agep = {
    '100': '99'
}
race2rac1p = {
    '10': '1',
    '20': '2',
    '21': '2',
    '22': '2',
    '23': '2',
    '24': '2',
    '30': '3',
    '31': '3',
    '40': '6',
    '41': '6',
    '42': '6',
    '43': '6',
    '44': '6',
    '45': '6',
    '46': '6',
    '47': '6',
    '48': '6',
    '49': '6',
    '50': '9',
    '51': '9',
    '52': '9',
    '53': '9',
    '54': '9',
    '55': '9',
    '60': '8',
    '61': '8',
    '99': '8'
}


def translate(iso3):
    code = iso3
    pp_csvs = _find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    hh_ids, hid2hincome = _translate_pp(pp_csvs, code)
    _cross_check_hids(iso3, hh_ids)
    _translate_hh(pp_csvs, hid2hincome, code)
    aid.touch_require_file(code, 'schools')
    aid.touch_require_file(code, 'workplaces')


def _translate_pp(pp_csvs, code):
    pp_csv = aid.output_csv_synth_file_path(code, 'people')
    gq_pp_csv = aid.output_csv_synth_file_path(code, 'gq_people')
    hh_ids, hid2hincome = _save_pp_as_csv(pp_csvs, pp_csv, gq_pp_csv)
    _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv)
    return hh_ids, hid2hincome


def _cross_check_hids(iso3, hh_ids):
    hh_csvs = _find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix)
    ref_hh_ids = _to_household_ids(hh_csvs)
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        txt = 'Household IDs from people and household inputs are different:'
        raise Exception(txt, difference)


def _translate_hh(pp_csvs, hid2hincome, code):
    hh_csv = aid.output_csv_synth_file_path(code, 'households')
    gq_csv = aid.output_csv_synth_file_path(code, 'gq')
    _save_hh_as_csv(pp_csvs, hid2hincome, hh_csv, gq_csv)
    _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv)


def _save_pp_as_csv(in_file_paths, pp_path, gq_path):
    """  0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
         5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
        10 latitude,AGE,SEX,RACE,SCHOOL,
        15 INCTOT,SYNTHETIC_PID+made-sporder,made-age,made-empty,
        20 made-race """
    hhtype_column = 5
    hid_column = 8
    age_column = 11
    race_column = 13
    inctot_column = 15
    more_header = 'made-sporder,made-age,made-empty,made-race'
    columns = 21
    hid2cnt = {}
    hid2hincome = {}
    aid.mkdir(pp_path)
    aid.mkdir(gq_path)
    with open(pp_path, 'w') as pp_csv, open(gq_path, 'w') as gq_csv:
        print('writing', os.path.abspath(pp_path), os.path.abspath(gq_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for raw in fin:
                    line = raw.rstrip('\n')
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count == 1:
                            row = ','.join([line, more_header])
                            aid.write_and_check_columns(pp_csv, row, columns)
                            aid.write_and_check_columns(gq_csv, row, columns)
                        continue
                    cells = line.split(',')
                    hid = cells[hid_column]
                    order = hid2cnt.get(hid, 0) + 1
                    age = cells[age_column]
                    race = cells[race_column]
                    row = ','.join([
                        line,
                        str(order),
                        _to_agep(age),
                        '',
                        str(race2rac1p.get(race, race))
                    ])
                    csv = gq_csv if cells[hhtype_column] == '11' else pp_csv
                    aid.write_and_check_columns(csv, row, columns)
                    hid2cnt[hid] = order
                    income = int('0' + cells[inctot_column])
                    hid2hincome[hid] = hid2hincome.get(hid, 0) + income
    return hid2cnt.keys() | set(), hid2hincome


def _to_household_ids(in_file_paths):
    """ COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
        HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
        latitude """
    hid_column = 8
    hids = set()
    for in_file_path in in_file_paths:
        with open(in_file_path, 'r') as fin:
            print('reading', in_file_path)
            for line in fin:
                cells = line.split(',')
                hids.add(cells[hid_column])
    return hids


def _save_hh_as_csv(in_file_paths, hid2hincome, hh_path, gq_path):
    """  0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
         5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
        10 latitude,AGE,SEX,RACE,SCHOOL,
        15 INCTOT,SYNTHETIC_PID+made-age,made-race,made-income,
        20 made-empty """
    persons_column = 3
    hhtype_column = 5
    hid_column = 8
    age_column = 11
    race_column = 13
    more_header = 'made-age,made-race,made-income,made-empty'
    columns = 21
    hids = set()
    aid.mkdir(hh_path)
    aid.mkdir(gq_path)
    with open(hh_path, 'w') as hh_csv, open(gq_path, 'w') as gq_csv:
        abspath = os.path.abspath
        print('writing', abspath(hh_path), abspath(gq_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for raw in fin:
                    line = raw.strip('\n')
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count == 1:
                            row = ','.join([line, more_header])
                            aid.write_and_check_columns(hh_csv, row, columns)
                            aid.write_and_check_columns(gq_csv, row, columns)
                        continue
                    cells = line.split(',')
                    hid = cells[hid_column]
                    if hid not in hids:
                        hids.add(hid)
                        age = cells[age_column]
                        race = cells[race_column]
                        row = ','.join([
                            line,
                            _to_agep(age),
                            str(race2rac1p.get(race, race)),
                            str(hid2hincome[hid]),
                            ''
                        ])
                        csv = gq_csv if cells[hhtype_column] == '11' else hh_csv
                        aid.write_and_check_columns(csv, row, columns)
                        persons = cells[persons_column]
                        if int(persons) > 20:
                            msg = 'Warning: max persons of NP is 20 but got'
                            print(msg, persons, ':', row)


def _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv):
    """ csv columns (input):
     0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
     5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    10 latitude,AGE,SEX,RACE,SCHOOL,
    15 INCTOT,SYNTHETIC_PID+made-sporder,made-age,made-empty,
    20 made-race
    text columns (output):
    sp_id,sp_hh_id,serialno,stcotrbg,age,
    sex,race,sporder,relate,sp_school_id,
    sp_work_id """
    pp_columns = [17, 9, 3, 8, 19, 13, 21, 18, 20, 20, 20]
    aid.reorder_and_check_header(pp_csv, pp_columns, 'synth_people.txt-ipums')
    # text columns (output):
    # sp_id,sp_gq_id,sporder,age,sex
    gq_pp_columns = [17, 9, 18, 19, 13]
    aid.reorder_and_check_header(gq_pp_csv, gq_pp_columns,
                                 'synth_gq_people.txt-ipums')


def _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv):
    """ csv columns (input):
     0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
     5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    10 latitude,AGE,SEX,RACE,SCHOOL,
    15 INCTOT,SYNTHETIC_PID+made-age,made-race,made-income,
    20 made-empty
    text columns (output):
    sp_id,serialno,stcotrbg,hh_race,hh_income,
    hh_size,hh_age,latitude,longitude """
    hh_columns = [9, 3, 8, 19, 20, 4, 18, 11, 10]
    aid.reorder_and_check_header(hh_csv, hh_columns,
                                 'synth_households.txt-ipums')
    # text columns (output):
    # sp_id,gq_type,persons,stcotrbg,latitude,longitude
    gq_columns = [9, 21, 4, 8, 11, 10]
    aid.reorder_and_check_header(gq_csv, gq_columns, 'synth_gq.txt-ipums')


def _to_agep(age):
    return age2agep.get(age, age)


def _find_csvs_by_iso3_and_prefix(iso3, prefix):
    result = prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs_by_iso3_and_prefix(iso3, prefix)


def test():
    import filecmp
    prefix2csvs[conf.hh_prefix] = ['spew_sample/fji/household_ra.csv']
    prefix2csvs[conf.pp_prefix] = ['spew_sample/fji/people_ra.csv']
    translate('fji')
    actual = './populations/spew_1.2.0_fji'
    expected = './expected/spew_1.2.0_fji'
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