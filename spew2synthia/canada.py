import os

import aid
import conf
import spew

prefix2csvs = {}
age_group2age = {
    '1': '0',
    '2': '10',
    '3': '15',
    '4': '20',
    '5': '25',
    '6': '30',
    '7': '35',
    '8': '40',
    '9': '45',
    '10': '50',
    '11': '55',
    '12': '65',
    '13': '75',
    '88': '88' # TODO it should be 'Not available'
}

def find_csvs_by_iso3_and_prefix(iso3, prefix):
    result = prefix2csvs.get(prefix, None)
    if result:
        return result
    return spew.find_csvs_by_iso3_and_prefix(iso3, prefix)


def translate(iso3):
    code = iso3
    pp_csvs = find_csvs_by_iso3_and_prefix(iso3, conf.pp_prefix)

    pp_csv = synth_file_name(code, 'people')
    (hh_ids, sc_ids, wp_ids) = out_pp_file(pp_csvs, spew.pp_mapper, pp_csv)
    save_pp_as_text_with_reordering_columns(pp_csv)

    ref_hh_ids = out_ref_hh_file(find_csvs_by_iso3_and_prefix(iso3, conf.hh_prefix), spew.hh_mapper, os.devnull)  # out_file_name('ref_hh'))
    difference = hh_ids.difference(ref_hh_ids)
    if difference:
        raise Exception('Household IDs from people and household input files are different:' + str(difference))
    hh_csv = synth_file_name(code, 'households')
    out_hh_file(pp_csvs, spew.hh_mapper, hh_csv)
    save_hh_as_text_with_reordering_columns(hh_csv)

    aid.touch_file(out_file_name(code, 'schools').replace('.csv', '.txt'))
    aid.touch_file(out_file_name(code, 'workplaces').replace('.csv', '.txt'))
    aid.touch_file(synth_file_name(code, 'gq').replace('.csv', '.txt'))
    aid.touch_file(synth_file_name(code, 'gq_people').replace('.csv', '.txt'))


def save_hh_as_text_with_reordering_columns(hh_csv):
    # csv columns (input):
    # serialno,puma_id,stcotrbg,sp_id,longitude, latitude,AGEGRP,HRSWRK,IMMSTAT,hh_income,
    # MODE,OCC,POB,RELIGION,SEX, SYNTHETIC_PID,dummy,sex
    # text columns (output):
    # sp_id,serialno,stcotrbg,hh_race,hh_income,hh_size,hh_age,latitude,longitude
    aid.reorder(hh_csv, [4, 1, 3, 17, 10, 17, 17, 6, 5])


def save_pp_as_text_with_reordering_columns(pp_csv):
    # csv columns (input):
    # serialno,puma_id,stcotrbg,sp_hh_id,longitude, latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
    # MODE,OCC,POB,RELIGION,sex, sp_id,sporder,dummy,sex,age
    # text columns (output):
    # sp_id,sp_hh_id,serialno,stcotrbg,age,sex,race,sporder,relate,sp_school_id,sp_work_id,AGEGRP
    aid.reorder(pp_csv, [16, 4, 1, 3, 18, 19, 18, 17, 18, 18, 18, 7])
    # sp_id,sp_hh_id,serialno,stcotrbg,age,sex,race,sporder,relate,sp_school_id,sp_work_id
    #aid.reorder(pp_csv, [16, 4, 1, 3, 20, 19, 18, 17, 18, 18, 18])


def synth_file_name(code, type):
    return out_file_name(code, 'synth_' + type)


def out_file_name(code, name):
    out = '../populations'
    prefix = '/spew_1.2.0_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def out_pp_file(in_file_paths, mapper, out_file_path):
    # SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude, latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
    # MODE,OCC,POB,RELIGION,SEX, SYNTHETIC_PID+sporder,dummy,sex,age
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 3
    SEX_COLUMN = 14
    RELP_COLUMN = 6
    SCHOOL_COLUMN = 0
    WORKPLACE_COLUMN = 0
    AGEGRP_COLUMN = 6
    hid2cnt = {}
    hids = set()
    wp_ids = set()
    sc_ids = set()
    skips = 0
    aid.mkdir(out_file_path)
    reversed_sex = {'1':'2', '2':'1'}
    with open(out_file_path, 'w') as fout:
        file_count = 0
        for in_file_path in in_file_paths:
            with open(in_file_path, 'r') as fin:
                print('reading', in_file_path)
                for line in fin:
                    cells = line.rstrip('\n').split(',')
                    if line.startswith('SERIALNO'):
                        file_count += 1
                        if file_count > 1:
                            continue
                        cells.append('sporder,dummy,sex,age')
                    else:
                        hid = cells[HID_COLUMN]
                        if cells[RELP_COLUMN] == '0':
                            hids.add(hid)
                        order = hid2cnt.get(hid, 0)
                        order += 1
                        cells.append(str(order))
                        cells.append('')
                        sex = cells[SEX_COLUMN]
                        cells.append(reversed_sex.get(sex, sex))
                        agegroup = cells[AGEGRP_COLUMN]
                        cells.append(age_group2age.get(agegroup, agegroup))
                        hid2cnt[hid] = order
                        #school_id = cells[SCHOOL_COLUMN]
                        #sc_ids.add(school_id)
                        #workplace_id = cells[WORKPLACE_COLUMN]
                        #wp_ids.add(workplace_id)
                    row = ','.join([mapper(x) for x in cells])
                    fout.write(row + "\n")
    print('Skipped', skips, 'rows due to private schools')
    return hid2cnt.keys() | set(), sc_ids, wp_ids


def out_ref_hh_file(in_file_paths, mapper, out_file_path):
    # SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude, latitude
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 3
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
    # SERIALNO,puma_id,place_id,SYNTHETIC_HID,longitude, latitude,AGEGRP,HRSWRK,IMMSTAT,INCTAX,
    # MODE,OCC,POB,RELIGION,SEX, SYNTHETIC_PID+dummy
    print('writing', os.path.abspath(out_file_path))
    HID_COLUMN = 3
    aid.mkdir(out_file_path)
    hids = set()
    with open(out_file_path, 'w') as fout:
        file_count = 0
        for in_file_path in in_file_paths:
            print('reading', in_file_path)
            with open(in_file_path, 'r') as fin:
                for line in fin:
                    cells = line.strip('\n').split(',')
                    if line.startswith('SERIALNO'):
                        cells.append('dummy')
                        file_count += 1
                        if file_count > 1:
                            continue
                    else:
                        cells.append('')
                    hid = cells[HID_COLUMN]
                    if hid not in hids or hid == 'SYNTHETIC_HID':
                        hids.add(hid)
                        mapped_cells = [mapper(x) for x in cells]
                        row = ','.join(mapped_cells)
                        fout.write(row + '\n')


def test():
    prefix2csvs[conf.hh_prefix] = ['spew_sample/can/household_4620440.00.csv']
    prefix2csvs[conf.pp_prefix] = ['spew_sample/can/people_4620440.00.csv']
    import filecmp
    translate('can')
    actual = '../populations/spew_1.2.0_can'
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