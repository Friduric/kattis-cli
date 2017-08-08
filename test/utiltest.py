from pathlib import Path

def read_file(fpath, mode='r'):
    with open(fpath.as_posix(), mode) as f:
        data = f.read()
    return data


def get_rule_directory():
    return Path('testrules')


def get_rule_file(fname):
    return get_rule_directory() / fname
