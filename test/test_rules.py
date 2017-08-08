import rules
import pytest
from utiltest import *


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


def test_only_towards_necessary():
    rule_path = get_rule_file('test_only_towards_necessary.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1

    rule = ruleset.rules[0]
    assert rule.towards == 'only-towards-necessary'
    assert rule.points
    assert rule.needs


def test_inspect_simple_rule():
    rule_path = get_rule_file('test_inspect_simple_rule.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1

    rule = ruleset.rules[0]
    assert rule.needs == "inspect-need"
    assert rule.towards == "inspect-towards"
    assert rule.points == 1
    assert rule.deadline == "01-01-2017 08:00"
    assert rule.name == "Inspect Rule"
    assert rule.late == "halved"


def test_inspect_complex_rule():
    rule_path = get_rule_file('test_inspect_complex_rule.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1

    need_expression = {
        "OR": [
            False,
            {
                "positive": {
                    "get": "some-other-goal"
                }
            },
            {
                ">": {
                    "lhs": 4,
                    "rhs": 2
                }
            }
        ]
    }

    value_expression = {
        "+": [
            1,
            2,
            3,
            {
                "*": [
                    4,
                    2
                ]
            },
            {
                "-": [
                    4,
                    3,
                    1
                ]
            },
            {
                "/": [
                    42,
                    21
                ]
            },
            {
                "get": "another-goal"
            },
            {
                "MAX": [1, 2, 1]
            }
        ]
    }

    rule = ruleset.rules[0]
    assert rule.needs == need_expression
    assert rule.towards == "inspect-complex-towards"
    assert rule.points == value_expression
