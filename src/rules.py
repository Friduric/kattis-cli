import collections
import json
import util


Ruleset = collections.namedtuple('Ruleset', 'rules')


def make_ruleset():
    return Ruleset([])


def ruleset_add_rule(ruleset, rule):
    ruleset.rules.append(rule)


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

def parse_json(json):
    # Create ruleset and add rules from json
    ruleset = make_ruleset()
    add_rule = lambda rule: ruleset_add_rule(ruleset, rule)
    rules = json.get('rules', [])
    util.map_now(add_rule, rules)

    # Find all includes and include their rules as well
    include_group = get_include_group(json.get('includes', []))
    def add_rules_from_file(fpath):
        util.map_now(add_rule, get_rules_from_file(fpath))
    util.map_now(add_rules_from_file, include_group)

    return ruleset


def parse_string(content):
    parsed = json.loads(content)
    return parse_json(parsed)


def parse_file(fpath):
    with open(fpath, 'r') as f:
        parsed = json.load(f)
    return parse_json(parsed)
