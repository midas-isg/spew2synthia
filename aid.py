from datetime import datetime
from itertools import cycle
import os
import sys
import subprocess
import traceback
# File System
################################################################################


def mkdir(out_file_path):
    dirname = os.path.dirname(out_file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def make_path(path):
    mkdir(path)
    return path


def touch_require_file(code, record_type):
    touch_file(output_csv_file_path(code, record_type).replace('.csv', '.txt'))


def touch_file(filename):
    open(filename, 'a').close()


def output_csv_synth_file_path(code, record_type):
    return output_csv_file_path(code, 'synth_' + record_type)


def output_csv_file_path(code, name):
    out = 'populations'
    prefix = '/spew_1.2.0_' + code
    return out + prefix + prefix + '_' + name + '.csv'


def reorder_and_check_header(csv, columns, header_filename):
    out_file_path = csv.replace('.csv', '.txt')
    print('writing', os.path.abspath(out_file_path))
    header_dir = 'populations_headers/'
    print('reading', csv)
    header_path = header_dir + header_filename
    with open(csv, 'r') as fin, open(header_path, 'r') as header_file:
        expected = header_file.readline().strip('\n')
        line = fin.readline()
        cells = line.strip('\n').split(',')
        header = ','.join(cells[i - 1] for i in columns)
        if not expected == header:
            raise Exception(csv, 'must have header of', expected,
                            'but got', header)
    with open(out_file_path, 'w') as f:
        with open(header_dir + header_filename.split('-')[0], 'r') as h:
            f.write(h.readline().strip('\n') + '\n')
            f.flush()
        template = '","'.join(['$' + str(x) for x in columns])
        subprocess.run(["awk",
                        'BEGIN { FS = "," } NR >= 2{ print ' + template + '}',
                        csv], stdout=f)
    delete(csv)


def delete(file):
    print('deleting', file)
    os.remove(file)


def write_and_check_columns(fout, row, columns):
    actual_columns = len(row.split(','))
    if not actual_columns == columns:
        print(flush=True)
        raise Exception('Expected # columns is', columns, \
                        'but got', actual_columns, ':', row)
    fout.write(row + "\n")
# Logs
################################################################################


def log_time(s=''):
    print(datetime.now(), s, flush=True)


def log_error(e):
    print(flush=True)
    tbs = traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                     e, e.__traceback__)
    for tb in tbs:
        print(tb, file=sys.stderr, flush=True)
# Strings
################################################################################


def str_cycle(iter):
    return cycle(str(x) for x in iter)

