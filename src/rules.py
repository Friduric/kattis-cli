import collections
import json
import util
import os


##########################################
# Ruleset                                #
##########################################

Ruleset = collections.namedtuple('Ruleset', 'rules')


def make_ruleset():
    return Ruleset([])


def ruleset_add_rule(ruleset, rule):
    ruleset.rules.append(rule)


##########################################
# Rule                                   #
##########################################


Rule = collections.namedtuple('Rule', 'needs towards points deadline name late')


def make_rule(needs, towards, points, deadline, name, late):
    return Rule(needs, towards, points, deadline, name, late)


def make_rule_from_json(json):
    def crash_get(key):
        return json[key]

    def get_or_default(key, default):
        return json.get(key, default)

    mandatory = ['towards']
    nonmandatory = [('deadline', ''), ('name', ''), ('late', ''), ('needs', True), ('points', 1)]

    towards = crash_get(mandatory[0])
    deadline, name, late, needs, points = util.starmap_now(get_or_default, nonmandatory)
    return make_rule(needs, towards, points, deadline, name, late)


##########################################
# File Helpers                           #
##########################################


def get_element_from_file(fpath, key, default):
    with open(fpath, 'r') as f:
        parsed = json.load(f)
    return parsed.get(key, default)


def get_includes_from_file(fpath):
    return get_element_from_file(fpath, 'includes', [])


def get_rules_from_file(fpath):
    return get_element_from_file(fpath, 'rules', [])


def get_include_group(includes):
    included_files = set()
    queue = collections.deque(list(includes)) # Copy into deque
    while queue:
        current = queue.popleft()
        if current in included_files:
            continue
        included_files.add(current)
        added_includes = get_includes_from_file(current)
        queue.extend(added_includes)
    return list(included_files)


##########################################
# Parsing                                #
##########################################


def parse_json(json, _from_file=''):
    # Create ruleset and add rules from json
    ruleset = make_ruleset()
    add_rule = lambda rule: ruleset_add_rule(ruleset, make_rule_from_json(rule))
    rules = json.get('rules', [])
    util.map_now(add_rule, rules)

    # Find all includes and include their rules as well
    include_group = get_include_group(json.get('includes', []))
    def is_not_origin(fpath):
        return os.path.abspath(fpath) != os.path.abspath(_from_file)
    def add_rules_from_file(fpath):
        util.map_now(add_rule, get_rules_from_file(fpath))

    include_group_except_self = filter(is_not_origin, include_group)
    util.map_now(add_rules_from_file, include_group_except_self)

    return ruleset


def parse_string(content):
    parsed = json.loads(content)
    return parse_json(parsed)


def parse_file(fpath):
    with open(fpath, 'r') as f:
        parsed = json.load(f)
    return parse_json(parsed, _from_file=fpath)
