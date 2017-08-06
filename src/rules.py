import collections
import json
import util


Ruleset = collections.namedtuple('Ruleset', 'rules')


def make_ruleset():
    return Ruleset([])


def ruleset_add_rule(ruleset, rule):
    ruleset.rules.append(rule)


def parse_json(json):
    ruleset = make_ruleset()
    add_rule = lambda rule: ruleset_add_rule(ruleset, rule)
    iterator = map(add_rule, json.get('rules', []))

    util.consume(iterator)
    return ruleset


def parse_string(content):
    parsed = json.loads(content)
    return parse_json(parsed)


def parse_file(fpath):
    with open(fpath, 'r') as f:
        parsed = json.load(f)
    return parse_json(parsed)
