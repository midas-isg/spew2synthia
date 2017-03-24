from datetime import datetime
import sys
import os

import aid
import conf
import run


def print_time():
    print(datetime.now())


path = 'logs/'
aid.mkdir(path)
common = open(path + 'common.' + str(datetime.now()), 'w')
sys.stdout = common
sys.stderr = common
#run.main('01077')
#run.main('56')
#run.main('42')
files = os.listdir(conf.path_usa)
#print(files)
for name in files:
    if name == 'input':
        continue
    stdout = path + name + '.out'
    if os.path.exists(stdout):
        print(stdout, 'already exists. Delete it if you want to rerun.')
        continue
    sys.stdout = open(stdout, 'w')
    sys.stderr = open(path + name + '.err', 'w')
    print_time()
    try:
        run.main(name)
    except Exception as e:
        import traceback
        tbs = traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                               e, e.__traceback__)
        for tb in tbs:
            print(tb, file=sys.stderr, flush=True)
    finally:
        print_time()
        sys.stdout = common
        sys.stderr = common
