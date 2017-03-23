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
for name in files:
    if name == 'input':
        continue
    path = 'std/'
    aid.mkdir(path)
    sys.stdout = open(path + name + '.out', 'w')
    sys.stderr = open(path + name + '.err', 'w')
    print_time()
    try:
        run.main(name)
    finally:
        print_time()
