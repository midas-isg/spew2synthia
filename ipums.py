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
    pp_csvs = find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    pp_csv = synth_file_name(code, 'people')
    gq_pp_csv = synth_file_name(code, 'gq_people')
    (hh_ids, sc_ids, wp_ids, hid2hincome) = out_pp_file(pp_csvs, spew.pp_mapper, pp_csv, gq_pp_csv)
    save_pp_as_text_with_reordering_columns(pp_csv, gq_pp_csv)

    ref_hh_ids = out_ref_hh_file(find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name(code, 'households')
    gq_csv = synth_file_name(code, 'gq')
    out_hh_file(pp_csvs, spew.hh_mapper, hid2hincome, hh_csv, gq_csv)
    save_hh_as_text_with_reordering_columns(hh_csv, gq_csv)

    aid.touch_file(out_file_name(code, 'schools').replace('.csv', '.txt'))
    aid.touch_file(out_file_name(code, 'workplaces').replace('.csv', '.txt'))


def save_pp_as_text_with_reordering_columns(pp_csv, gq_pp_csv):
    # csv columns (input):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID+made-sporder,made-age,made-empty,
    # made-race
    # text columns (output):
    # sp_id,sp_hh_id,serialno,stcotrbg,age,sex,race,sporder,relate,sp_school_id,sp_work_id
    aid.reorder_and_verify_header(pp_csv, [17, 9, 3, 8, 19, 13, 21, 18, 20, 20, 20], 'synth_people.txt-ipums')
    # text columns (output):
    # sp_id,sp_gq_id,sporder,age,sex
    aid.reorder_and_verify_header(gq_pp_csv, [17, 9, 18, 19, 13], 'synth_gq_people.txt-ipums')


def save_hh_as_text_with_reordering_columns(hh_csv, gq_csv):
    # csv columns (input):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID+made-age,made-race,made-income,
    # made-empty
    # text columns (output):
    # sp_id,serialno,stcotrbg,hh_race,hh_income,hh_size,hh_age,latitude,longitude
    aid.reorder_and_verify_header(hh_csv, [9, 3, 8, 19, 20, 4, 18, 11, 10], 'synth_households.txt-ipums')
    # text columns (output):
    # sp_id,dummy,hh_size,stcotrbg,latitude,longitude
    # sp_id,gq_type,persons,stcotrbg,latitude,longitude
    aid.reorder_and_verify_header(gq_csv, [9, 21, 4, 8, 11, 10], 'synth_gq.txt-ipums')


def find_csvs_by_iso3_and_prefix(iso3, prefix):
    result = prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs_by_iso3_and_prefix(iso3, prefix)


def synth_file_name(code, type):
    return out_file_name(code, 'synth_' + type)


def out_file_name(code, name):
    out = 'populations'
    prefix = '/spew_1.2.0_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def to_agep(age):
    return age2agep.get(age, age)


def out_pp_file(in_file_paths, mapper, pp_path, gq_path):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID+made-sporder,made-age,made-empty,
    # made-race
    HHTYPE_COLUMN = 5
    HID_COLUMN = 8
    AGE_COLUMN = 11
    RACE_COLUMN = 13
    INCTOT_COLUMN = 15
    columns = 21
    hid2cnt = {}
    hid2hincome = {}
    wp_ids = set()
    sc_ids = set()
    aid.mkdir(pp_path)
    aid.mkdir(gq_path)
    with open(pp_path, 'w') as pp_csv, open(gq_path, 'w') as gq_csv:
        print('writing', os.path.abspath(pp_path), os.path.abspath(gq_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count == 1:
                            cells.append('made-sporder,made-age,made-empty,made-race')
                            row = ','.join(cells)
                            aid.write_and_check_number_of_columns(pp_csv, row, columns)
                            aid.write_and_check_number_of_columns(gq_csv, row, columns)
                        continue
                    hid = cells[HID_COLUMN]
                    order = hid2cnt.get(hid, 0) + 1
                    hid2cnt[hid] = order
                    income = int('0' + cells[INCTOT_COLUMN])
                    hid2hincome[hid] = hid2hincome.get(hid, 0) + income
                    cells.append(str(order))
                    age = cells[AGE_COLUMN]
                    cells.append(to_agep(age))
                    cells.append('')
                    race = cells[RACE_COLUMN]
                    cells.append(str(race2rac1p.get(race, race)))
                    row = ','.join(cells)
                    htype = cells[HHTYPE_COLUMN]
                    if htype == '11':
                        aid.write_and_check_number_of_columns(gq_csv, row, columns)
                    else:
                        aid.write_and_check_number_of_columns(pp_csv, row, columns)
    return hid2cnt.keys() | set(), sc_ids, wp_ids, hid2hincome


def out_ref_hh_file(in_file_paths):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude, latitude
    HID_COLUMN = 8
    hids = set()
    for in_file_path in in_file_paths:
        with open(in_file_path, 'r') as fin:
            print('reading', in_file_path)
            for line in fin:
                cells = line.split(',')
                hids.add(cells[HID_COLUMN])
    return hids


def out_hh_file(in_file_paths, mapper, hid2hincome, out_file_path, gq_path):
    # COUNTRY,YEAR,SERIALNO,PERSONS,puma_id, HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    # latitude,AGE,SEX,RACE,SCHOOL, INCTOT,SYNTHETIC_PID+made-age,made-race,made-income,
    # made-empty
    PERSONS_COLUMN = 3
    HHTYPE_COLUMN = 5
    HID_COLUMN = 8
    AGE_COLUMN = 11
    RACE_COLUMN = 13
    columns = 21
    aid.mkdir(out_file_path)
    hids = set()
    with open(out_file_path, 'w') as fout, open(gq_path, 'w') as gq_csv:
        print('writing', os.path.abspath(out_file_path), os.path.abspath(gq_path))
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.strip('\n').split(',')
                    if line.startswith('COUNTRY'):
                        file_count += 1
                        if file_count == 1:
                            row = ','.join(cells) + ',made-age,made-race,made-income,made-empty'
                            aid.write_and_check_number_of_columns(fout, row, columns)
                            aid.write_and_check_number_of_columns(gq_csv, row, columns)
                        continue
                    hid = cells[HID_COLUMN]
                    if hid not in hids:
                        hids.add(hid)
                        age = cells[AGE_COLUMN]
                        cells.append(to_agep(age))
                        race = cells[RACE_COLUMN]
                        cells.append(str(race2rac1p.get(race, race)))
                        cells.append(str(hid2hincome[hid]))
                        cells.append('')
                        row = ','.join(cells)
                        htype = cells[HHTYPE_COLUMN]
                        if htype == '11':
                            aid.write_and_check_number_of_columns(gq_csv, row, columns)
                        else:
                            aid.write_and_check_number_of_columns(fout, row, columns)
                        persons = cells[PERSONS_COLUMN]
                        if int(persons) > 20:
                            msg = 'Warning: max persons according to NP is 20 but got'
                            print(msg, persons, ':', row, file=sys.stderr, flush=True)


def test():
    import filecmp
    prefix2csvs[conf.hh_prefix] = ['spew_sample/fji/household_ra.csv']
    prefix2csvs[conf.pp_prefix] = ['spew_sample/fji/people_ra.csv']
    translate('fji')
    actual = './populations/spew_1.2.0_fji'
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