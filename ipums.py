from collections import OrderedDict
import os
import sys

import aid
import conf
import spew
max_hid_len = 30
max_pid_len = 54
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
        20 made-race,made-hid """
    hhtype_column = 5
    hid_column = 8
    age_column = 11
    race_column = 13
    inctot_column = 15
    pid_column = 16
    more_header = 'made-sporder,made-age,made-empty,made-race,made-hid,made-pid'
    columns = 23
    hid2cnt = {}
    hid2hincome = {}
    pid2shortened = OrderedDict()
    pids = set()
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
                    pid = cells[pid_column]
                    row = ','.join([
                        line,
                        str(order),
                        _to_agep(age),
                        '',
                        str(race2rac1p.get(race, race)),
                        _shorten(hid, max_hid_len),
                        _shorten_then_store(pid, max_pid_len, pid2shortened)
                    ])
                    pids.add(pid)
                    csv = gq_csv if cells[hhtype_column] == '11' else pp_csv
                    aid.write_and_check_columns(csv, row, columns)
                    hid2cnt[hid] = order
                    income = int('0' + cells[inctot_column])
                    hid2hincome[hid] = hid2hincome.get(hid, 0) + income
    prefix = pp_path.replace('synth_people.csv', '')
    _save_shortened_hid_mapping(pid2shortened, prefix + 'pid_mapping.csv')
    _check_duplicate_shortened_id(pid2shortened, pids)
    return (hid2cnt.keys() | set()), hid2hincome


def _save_shortened_hid_mapping(hid2shortened, file_path):
    if not hid2shortened:
        return
    with open(file_path, 'w') as mapping:
        mapping.write('original_id,shortened_id\n')
        for k, v in hid2shortened.items():
            mapping.write(k + ',' + v + '\n')


def _check_duplicate_shortened_id(id2shortened, ids):
    if not id2shortened:
        return
    short2ids = {}
    for id, short in id2shortened.items():
        short2ids.setdefault(short, set()).add(id)
    log_if_not_empty(
        [short for short, ids in short2ids.items() if len(ids) > 1],
        'shortened HID duplicates among themselves')
    log_if_not_empty(
        [short for id, short in id2shortened.items() if short in ids],
        'shortened HID duplicates with HIDs')


def log_if_not_empty(dup, msg):
    if dup:
        aid.eprint(msg, dup)


def _shorten_then_store(id, n, id2shorten_id):
    if len(id) <= n:
        return id
    shorten = _shorten(id, n)
    id2shorten_id[id] = shorten
    return shorten


def _shorten(id, n):
    id_len = len(id)
    return id[id_len - n:]


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
        20 made-empty,made-hid """
    persons_column = 3
    hhtype_column = 5
    hid_column = 8
    age_column = 11
    race_column = 13
    more_header = 'made-age,made-race,made-income,made-empty,made-hid'
    columns = 22
    hids = set()
    hid2shorten_hid = OrderedDict()
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
                            '',
                            _shorten_then_store(hid, max_hid_len, hid2shorten_hid)
                        ])
                        csv = gq_csv if cells[hhtype_column] == '11' else hh_csv
                        aid.write_and_check_columns(csv, row, columns)
                        persons = cells[persons_column]
                        if int(persons) > 20:
                            msg = 'Warning: max persons of NP is 20 but got'
                            print(msg, persons, ':', row)
        prefix = hh_path.replace('synth_households.csv', '')
        _save_shortened_hid_mapping(hid2shorten_hid, prefix + 'hid_mapping.csv')
        _check_duplicate_shortened_id(hid2shorten_hid, hids)



def _save_pp_as_txt_with_reordering_columns(pp_csv, gq_pp_csv):
    """ csv columns (input):
     0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
     5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    10 latitude,AGE,SEX,RACE,SCHOOL,
    15 INCTOT,SYNTHETIC_PID+made-sporder,made-age,made-empty,
    20 made-race,made-hid
    text columns (output):
    sp_id,sp_hh_id,serialno,stcotrbg,age,
    sex,race,sporder,relate,sp_school_id,
    sp_work_id """
    pp_columns = [17, 22, 3, 8, 19, 13, 21, 18, 20, 20, 20]
    aid.reorder_and_check_header(pp_csv, pp_columns, 'synth_people.txt-ipums')
    # text columns (output):
    # sp_id,sp_gq_id,sporder,age,sex
    gq_pp_columns = [17, 22, 18, 19, 13]
    aid.reorder_and_check_header(gq_pp_csv, gq_pp_columns,
                                 'synth_gq_people.txt-ipums')


def _save_hh_as_txt_with_reordering_columns(hh_csv, gq_csv):
    """ csv columns (input):
     0 COUNTRY,YEAR,SERIALNO,PERSONS,puma_id,
     5 HHTYPE,PERNUM,place_id,SYNTHETIC_HID,longitude,
    10 latitude,AGE,SEX,RACE,SCHOOL,
    15 INCTOT,SYNTHETIC_PID+made-age,made-race,made-income,
    20 made-empty,made-hid
    text columns (output):
    sp_id,serialno,stcotrbg,hh_race,hh_income,
    hh_size,hh_age,latitude,longitude """
    hh_columns = [22, 3, 8, 19, 20, 4, 18, 11, 10]
    aid.reorder_and_check_header(hh_csv, hh_columns,
                                 'synth_households.txt-ipums')
    # text columns (output):
    # sp_id,gq_type,persons,stcotrbg,latitude,longitude
    gq_columns = [22, 21, 4, 8, 11, 10]
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
    global max_hid_len
    max_hid_len = 4
    global max_pid_len
    max_pid_len = 7
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