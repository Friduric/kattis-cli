from pathlib import Path
import rules
import pytest


def read_file(fpath, mode='r'):
    with open(fpath.as_posix(), mode) as f:
        data = f.read()
    return data


def get_rule_directory():
    return Path('rules')


def get_rule_file(fname):
    return get_rule_directory() / fname


def test_hello_world():
    assert 1 == 1


def test_load_json_from_string():
    rule_path = get_rule_file('test_load_json_from_string_rules.json')
    content = str(read_file(rule_path))
    ruleset = rules.parse_string(content)
    assert len(ruleset.rules) == 1


def test_load_json_from_file():
    rule_path = get_rule_file('test_load_json_from_file_rules.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1


def test_load_json_with_include():
    rule_path = get_rule_file('test_load_json_with_include_rules_1.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1


# Should only include like 2 files, if this takes longer than 10
# seconds and "runs as it should" then we have bigger problems....
@pytest.mark.timeout(10)
def test_circular_include():
    rule_path = get_rule_file('test_load_circular_import_1.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 2
