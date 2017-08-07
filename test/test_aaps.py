import aaps
import rules
import resolver
import util
from utiltest import *

def test_kattis_result():
    result = aaps.KattisResult()
    result.add_AC('helloworld', '01-01-2017 08:00')
    result.add_WA('helloworld', '01-01-2017 07:00')
    assert len(result.AC) == 1
    assert len(result.WA) == 1
    assert result.AC[0].id == 'helloworld'
    assert result.WA[0].id == 'helloworld'


def test_use_checker_and_handler():
    rule_path = get_rule_file('test_use_checker_and_handler.json')
    ruleset = rules.parse_file(rule_path.as_posix())
    assert len(ruleset.rules) == 2

    kattis = aaps.KattisResult()
    kattis.add_AC('testproblem', '01-01-2017 08:00')
    kattis.add_WA('testproblem2', '01-01-2017 08:00')

    context = resolver.make_context()
    plugins = kattis.get_plugins()
    func = lambda c, h: resolver.context_add_plugin(context, c, h)
    util.starmap_now(func, plugins)
    result = resolver.resolve(ruleset, context)
    assert len(result.goals) == 2
    assert any(goal.points == 1 and goal.id == 'test-problem' for goal in result.goals)
    assert any(goal.points == 0 and goal.id == 'test-problem-2' for goal in result.goals)
