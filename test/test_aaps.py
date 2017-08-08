import aaps
import rules
import resolver
import util
from utiltest import *


def get_ruleset_from_file(fpath):
    rule_path = get_rule_file(fpath)
    return rules.parse_file(rule_path.as_posix())


def resolve_for_result(kattis, ruleset):
    context = resolver.make_context()
    plugins = kattis.get_plugins()
    func = lambda c, h: resolver.context_add_plugin(context, c, h)
    util.starmap_now(func, plugins)
    return resolver.resolve(ruleset, context)


def test_kattis_result():
    result = aaps.KattisResult()
    result.add_AC('helloworld', '01-01-2017 08:00')
    result.add_WA('helloworld', '01-01-2017 07:00')
    assert len(result.AC) == 1
    assert len(result.WA) == 1
    assert result.AC[0].id == 'helloworld'
    assert result.WA[0].id == 'helloworld'


def test_use_checker_and_handler():
    ruleset = get_ruleset_from_file('test_use_checker_and_handler.json')
    assert len(ruleset.rules) == 2

    kattis = aaps.KattisResult()
    kattis.add_AC('testproblem', '01-01-2017 08:00')
    kattis.add_WA('testproblem2', '01-01-2017 08:00')

    result = resolve_for_result(kattis, ruleset)

    assert len(result.goals) == 2
    assert any(goal.points == 1 and goal.id == 'test-problem' for goal in result.goals)
    assert any(goal.points == 0 and goal.id == 'test-problem-2' for goal in result.goals)

def test_after_deadline():
    ruleset = get_ruleset_from_file('test_after_deadline.json')
    assert len(ruleset.rules) == 1

    kattis = aaps.KattisResult()
    kattis.add_AC('testproblem', '01-01-2017 08:00')

    result = resolve_for_result(kattis, ruleset)

    assert len(result.goals) == 1
    assert result.goals[0].points == 1 # Halved from 2


def test_uppgift():
    ruleset = get_ruleset_from_file('test_uppgift.json')
    assert len(ruleset.rules) == 1

    kattis = aaps.KattisResult()
    kattis.add_AC('helloworld', '01-01-2017 07:00')
    kattis.add_AC('helloworld', '01-01-2017 07:00')

    result = resolve_for_result(kattis, ruleset)

    assert len(result.goals) == 1
    assert result.goals[0].points == 2
