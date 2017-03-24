from datetime import datetime
import sys
import os

import aid
import conf
import run


def print_time():
    print(datetime.now())


#run.main('01077')
#run.main('56')
#run.main('42')
files = os.listdir(conf.path_usa)
# print(files)
path = 'std/'
aid.mkdir(path)
common = open(path + 'common.' + str(datetime.now()), 'w')
sys.stdout = common
sys.stderr = common
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
        pass#run.main(name)
    finally:
        print_time()
        sys.stdout = common
        sys.stderr = common
