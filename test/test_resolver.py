import random
import rules
import resolver
from utiltest import *

def test_resolve_basic():
    rule_path = get_rule_file('test_resolve_basic.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 1

    context = resolver.make_context()
    result = resolver.resolve(ruleset, context)
    assert any(goal.name == 'resolve-basic-goal' and goal.points == 1
               for goal in result.goals)
    assert len(result.goals) == 1


def test_resolve_two_to_same():
    rule_path = get_rule_file('test_resolve_two_to_same.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 2

    context = resolver.make_context()
    result = resolver.resolve(ruleset, context)
    assert len(result.goals) == 1
    goal = result.goals[0]
    assert goal.name == 'resolve-two-of-same' and goal.points == 2 and \
        len(goal.resolved_rules) == 2 and len(goal.non_resolved_rules) == 0


def test_resolve_with_ordering():
    rule_path = get_rule_file('test_resolve_with_ordering.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 5

    context = resolver.make_context()
    result = resolver.resolve(ruleset, context)
    assert len(result.goals) == 5
    assert all(goal.points == 1 for goal in result.goals)
