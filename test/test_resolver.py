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


