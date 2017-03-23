import os


def mkdir(out_file_path):
    dirname = os.path.dirname(out_file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)