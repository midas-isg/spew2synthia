from datetime import datetime
import os
import sys

import aid
import conf
import us


def translate(states):
    print('Started translating states in', states)
    log_path = aid.make_path('logs/')
    with open(log_path + 'states.' + str(datetime.now()), 'w') as common:
        sys.stdout = common
        sys.stderr = common
        print('Translating', states)
        for state in states:
            if state == 'input':
                continue
            stdout = log_path + state + '.out'
            if os.path.exists(stdout):
                print(stdout, 'already exists. Delete it if you want to rerun.')
                continue
            aid.log_time('Translating ' + state)
            with open(stdout, 'w') as sys.stdout:
                with open(log_path + state + '.err', 'w') as sys.stderr:
                    aid.log_time()
                    try:
                        us.translate(state)
                    except Exception as e:
                        aid.log_error(e)
                    finally:
                        aid.log_time()
                        sys.stdout = common
                        sys.stderr = common



def test():
    translate(['56'])


if __name__ == "__main__":
    translate(os.listdir(conf.path_usa))