import collections
import json
import util


Ruleset = collections.namedtuple('Ruleset', 'rules')


def make_ruleset():
    return Ruleset([])


def ruleset_add_rule(ruleset, rule):
    ruleset.rules.append(rule)


def parse_string(content):
    parsed = json.loads(content)
    ruleset = make_ruleset()
    add_rule = lambda rule: ruleset_add_rule(ruleset, rule)
    iterator = map(add_rule, parsed.get('rules', []))

    util.consume(iterator)
    return ruleset


def parse_file(fpath):
    return []
