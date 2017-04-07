import glob
import conf
ISO3_CANADA = 'can'
test_pattern = None

def find_csvs_by_iso3_and_prefix(iso3, prefix):
    path = find_country_by_iso3(iso3)
    pattern_csv = path + '/**/{prefix}*.csv'
    pattern = pattern_csv.format(prefix=prefix)
    print("Finding", pattern)
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise Exception('No file starting with ' + prefix)
    print('Found', len(files), [p.split(iso3 + '/output/')[1] for p in files])
    return files


def find_country_by_iso3(iso3):
    files = find_countries(iso3)
    return files[0]


def find_all_countries():
    country_outputs = find_countries('*/output')
    return [o.replace('/output', '') for o in country_outputs]


def find_ipums_countries_ids():
    ids = [o.split('/')[-1] for o in find_all_countries()]
    ids.remove(ISO3_CANADA)
    return ids


def find_countries(iso3):
    pattern = conf.pattern_country.format(iso3=iso3)
    print("Finding", pattern)
    files = glob.glob(pattern, recursive=False)
    if not files:
        raise Exception('No directory for country ISO3 = ' + iso3)
    # print('Found', len(files), files)
    return files


def find_csvs(prefix, fips):
    state = fips[:2]
    return _find_csvs_by_state_and_prefix(state, prefix + fips)


def _find_csvs_by_state_and_prefix(state, prefix):
    pattern = conf.pattern_csv.format(state=state, prefix=prefix)
    if test_pattern:
        pattern = test_pattern.format(state=state, prefix=prefix)
    print("Finding", pattern)
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise Exception('No file starting with ' + prefix)
    state_output = conf.pattern_state_output.format(state=state)
    print('Found', len(files), [p.replace(state_output + '/', '') for p in files])
    return files


def test():
    global test_pattern
    test_pattern = 'spew_sample/usa/{prefix}*.csv'
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


def hh_mapper(x):
    return conf.hh_map.get(x, x)


def pp_mapper(x):
    return conf.pp_map.get(x, x)


def sc_mapper(x):
    return conf.sc_map.get(x, x)


def wp_mapper(x):
    return conf.wp_map.get(x, x)