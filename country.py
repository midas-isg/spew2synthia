from datetime import datetime
import os
import sys

import aid
import canada
import ipums
import spew


def translate(ids):
    print('Started translating countries in', ids)
    log_path = aid.make_path('logs/')
    with open(log_path + 'countries.' + str(datetime.now()), 'w') as common:
        sys.stdout = common
        sys.stderr = common
        print('Translating countries with ISO 3166-1 alpha-3 in ', ids)
        for iso3 in ids:
            if iso3 == 'input':
                continue
            stdout = log_path + iso3 + '.out'
            if os.path.exists(stdout):
                print(stdout, 'already exists. Delete it if you want to rerun.')
                continue
            aid.log_time('Translating ' + iso3)
            with open(stdout, 'w') as sys.stdout:
                with open(log_path + iso3 + '.err', 'w') as sys.stderr:
                    aid.log_time()
                    try:
                        if iso3 == spew.ISO3_CANADA:
                            canada.translate(iso3)
                        else:
                            ipums.translate(iso3)
                    except Exception as e:
                        aid.log_error(e)
                    finally:
                        aid.log_time()
                        sys.stdout = common
                        sys.stderr = common


def test():
    translate(['fji'])


if __name__ == "__main__":
    translate(spew.find_ipums_countries_ids())
    translate([spew.ISO3_CANADA])
