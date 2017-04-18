from datetime import datetime
import os
import sys

import aid
import canada
import ipums
import spew


def translate(ids):
    sys_stderr = sys.stderr
    sys_stdout = sys.stdout
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
    sys.stderr = sys_stderr
    sys.stdout = sys_stdout


def test():
    translate(['fji'])


def _create(ids):
    log_path = aid.make_path('logs/')
    for iso3 in ids:
        stdout = log_path + iso3 + '.out'
        aid.touch_file(stdout)


if __name__ == "__main__":
    translate(spew.find_all_country_ids_except_usa())
