from datetime import datetime
import os
import sys

import aid
import conf
import spew
import us


def to_county_id(csv):
    tokens = csv.split('/')
    county = tokens[-1].split('_')[-1][:5]
    return county


def translate(states):
    path = 'logs/'
    aid.mkdir(path)
    with open(path + 'countries.' + str(datetime.now()), 'w') as common:
        sys.stdout = common
        sys.stderr = common
        #print(states)
        for state in states:
            if state == 'input':
                continue
            aid.log_time('Translating ' + state)
            try:
                pp_csvs = spew.find_csvs(conf.pp_prefix, state)
                countries = set([to_county_id(csv) for csv in pp_csvs])
                print(countries, flush=True)
                for county in countries:
                    try:
                        prefix = path + state + '/'+ county
                        stdout = prefix + '.out'
                        aid.mkdir(stdout)
                        if os.path.exists(stdout):
                            print(stdout, 'already exists. Delete it if you want to rerun.')
                            continue
                        aid.log_time('Translating ' + county)
                        sys.stdout = open(stdout, 'w')
                        sys.stderr = open(prefix + '.err', 'w')
                        us.translate(county)
                    except Exception as e:
                        aid.log_error(e)
                    finally:
                        aid.log_time()
                        sys.stdout = common
                        sys.stderr = common
            except Exception as e:
                aid.log_error(e)
            finally:
                aid.log_time()
                sys.stdout = common
                sys.stderr = common
        aid.log_time('Done')


def test():
    translate(['10'])


if __name__ == "__main__":
    translate(os.listdir(conf.path_usa))