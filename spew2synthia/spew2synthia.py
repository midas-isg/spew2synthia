import sys
from datetime import datetime

import aid
import run

def print_time():
    print(datetime.now())


#run.main('01077')
#run.main('56')
#run.main('42')
for i in range(1, 11):
    name = "{:02d}".format(i)
    path = 'stdout/'
    aid.mkdir(path)
    sys.stdout = open(path + name + '.txt', 'w')
    print_time()
    try:
        run.main(name)
    finally:
        print_time()
