import glob
import conf


def find_csvs(prefix, fips):
    state = fips[:2]
    return _find_csvs_by_state_and_prefix(state, prefix + fips)


def _find_csvs_by_state_and_prefix(state, prefix):
    pattern = conf.pattern_csv.format(state=state, prefix=prefix)
    print("Finding", pattern)
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise Exception('No file starting with ' + prefix)
    state_output = conf.pattern_state_output.format(state=state)
    print('Found', len(files), [p.replace(state_output + '/', '') for p in files])
    return files


def test():
    county = '01077'
    county_hh_csvs = find_csvs(conf.hh_prefix, county)
    county_pp_csvs = find_csvs(conf.pp_prefix, county)
    check_consistent(county_hh_csvs, county_pp_csvs)


def check_consistent(csv_list1, csv_list2):
    set1 = set(x.replace(conf.hh_prefix, '', 1) for x in csv_list1)
    pp_set = set(x.replace(conf.pp_prefix, '', 1) for x in csv_list2)
    difference = set1.difference(pp_set)
    if difference:
        raise Exception()
