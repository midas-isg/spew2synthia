from datetime import datetime
import os
import sys
import traceback


def mkdir(out_file_path):
    dirname = os.path.dirname(out_file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def log_time(s=''):
    print(datetime.now(), s, flush=True)


def make_path(path):
    mkdir(path)
    return path


def log_error(e):
    tbs = traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                     e, e.__traceback__)
    for tb in tbs:
        print(tb, file=sys.stderr, flush=True)


