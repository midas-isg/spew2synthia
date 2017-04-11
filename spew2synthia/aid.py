from datetime import datetime
from itertools import cycle
import os
import sys
import subprocess
import traceback
# File System
########################################################################################################################


def mkdir(out_file_path):
    dirname = os.path.dirname(out_file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def make_path(path):
    mkdir(path)
    return path


def touch_file(filename):
    open(filename, 'a').close()


def reorder(csv, columns):
    out_file_path = csv.replace('.csv', '.txt')
    print('writing', os.path.abspath(out_file_path))
    print('reading', csv)
    f = open(out_file_path, 'w')
    template = '","'.join(['$' + str(x) for x in columns])
    subprocess.run(["awk", 'BEGIN { FS = "," } { print ' + template + '}', csv], stdout=f)
    delete(csv)


def delete(file):
    print('deleting', file)
    os.remove(file)

# Logs
########################################################################################################################


def log_time(s=''):
    print(datetime.now(), s, flush=True)


def log_error(e):
    tbs = traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                     e, e.__traceback__)
    for tb in tbs:
        print(tb, file=sys.stderr, flush=True)


#
def str_cycle(iter):
    return cycle(str(x) for x in iter)

