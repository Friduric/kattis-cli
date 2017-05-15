import json
import sys
from datetime import datetime
from collections import namedtuple, defaultdict

import submit

Rule = namedtuple('Rule', 'needs name points towards deadline after_deadline')

def make_rule(needs, name, points, towards, deadline, after_deadline):
    return Rule(needs, name, points, towards, deadline, after_deadline)

def get_time(sub):
    return sub[0]

def get_id(sub):
    return sub[1]

def get_name(sub):
    return sub[2]

def get_rules(rulefile='rules.json'):
    with open(rulefile, 'r') as f:
        content = f.read()
    rules = json.loads(content)['rules']
    collect = []
    for rule in rules:
        needs = rule['needs']
        name = rule.get('name', needs)
        points = int(rule['points'])
        towards = rule['towards']
        deadline = rule.get('deadline', '01-01-2517 00:00') # 500 years should be enough
        after_deadline = rule.get('after-deadline', 'halved')
        collect.append(make_rule(needs, name, points, towards, deadline, after_deadline))
    return collect

def time_compare(a, b):
    # a is expected to be on form DD-MM-YYYY HH:MM
    # b is expected to be on form YYYY-MM-DD HH:MM:SS
    # b can also be on the form HH:MM:SS, which means it was today
    # Check http://strftime.org/ for formatting
    lhs = datetime.strptime(a, '%d-%m-%Y %H:%M')
    try:
        rhs = datetime.strptime(b, '%Y-%m-%d %H:%M:%S')
    except:
        rhs = datetime.strptime(b, '%H:%M:%S')
        rhs = datetime.now().replace(hour=rhs.hour, minute=rhs.minute, second=rhs.second)
    return lhs < rhs

def count_points(submissions):
    solved = {}
    for submission in submissions:
        solved[get_id(submission)] = get_time(submission)
    func_map = {
        'halved': lambda x: x / 2.0
    }
    rules = get_rules()
    awarded = defaultdict(int)
    cnt = 0
    print()
    for rule in rules:
        if rule.needs in solved:
            points = float(rule.points)
            if time_compare(rule.deadline, solved[rule.needs]) and rule.after_deadline in func_map:
                points = func_map[rule.after_deadline](points)
            awarded[rule.towards] += points
            cnt += 1
            if cnt % 5 == 0:
                print('   {}   '.format('-'*40))
            print('{} solved at {} gives {} pts towards {}'.format(rule.name.ljust(30),
                                                                   solved[rule.needs].ljust(20),
                                                                   points,
                                                                   rule.towards))
    print('   {}   '.format('-'*40))
    for key in sorted(awarded):
        print('In {} you have {} pts'.format(key, awarded[key]))
    print('Remember to add points for the problem sessions you have done to LAB1!')

def get_earliest_ac_solutions(submissions):
    subs = set()
    collect = []
    for sub in reversed(submissions):
        if get_id(sub) not in subs:
            subs.add(get_id(sub))
            collect.append(sub)
    return collect

def main():
    try:
        cfg = submit.get_config()
    except submit.ConfigError as exc:
        print(exc)
        sys.exit(1)
    subs = submit.get_submissions_with_config(cfg)
    count_points(get_earliest_ac_solutions(subs))

if __name__ == '__main__':
    main()
