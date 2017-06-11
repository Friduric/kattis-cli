import json
import sys
from datetime import datetime
from collections import namedtuple, defaultdict

import submit

Rule = namedtuple('Rule', 'needs name points towards deadline after_deadline')

Submission = namedtuple('Submission', 'time problemid problemname user')

User = namedtuple('User', 'submissions name id')

def make_rule(needs, name, points, towards, deadline, after_deadline):
    return Rule(needs, name, points, towards, deadline, after_deadline)

def make_submission(time, problemid, problemname, user):
    return Submission(time, problemid, problemname, user)

def make_user(name, id):
    return User(submissions=[], name=name, id=id)

def user_add_submission(user, submission):
    user.submissions.append(submission)



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
        solved[submission.problemid] = submission.time
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
        print('In {} you have {} solved problems'.format(key, awarded[key]))
    print('Remember to add points for the problem sessions you have done to LAB1!')
    print()

def get_earliest_ac_solutions(submissions):
    subs = set()
    collect = []
    for sub in reversed(submissions):
        if sub.problemid not in subs:
            subs.add(sub.problemid)
            collect.append(sub)
    return collect

def count_for_me():
    try:
        cfg = submit.get_config()
    except submit.ConfigError as exc:
        print(exc)
        sys.exit(1)
    subs = submit.get_submissions_with_config(cfg)
    def sub_to_submission(sub):
        time, problem_id, problem_name = sub
        return make_submission(time=time, problemid=problem_id,
                               problemname=problem_name, user='me')
    submissions = [x for x in map(sub_to_submission, subs)]
    count_points(get_earliest_ac_solutions(submissions))

def count_session_data(session):
    # session = starttime, name, problems, results, length
    # results = [teamresult...]
    # teamresult = {'members': [member], 'solved_count': [0-9]+}
    output = defaultdict(int)
    for teamresult in session['results']:
        num_solved = teamresult['solved_count']
        for member in teamresult['members']:
            output[member] += num_solved
    return output

def print_session_data(sessions):
    for session in sessions:
        print(session)
        cnt = 0
        for key in sessions[session]:
            if sessions[session][key]:
                print('   {} - {}'.format(key.ljust(20), sessions[session][key]))
                cnt += 1
                if cnt % 3 == 0:
                    print('-'*30)
        print('*'*42)

def count_user_data(user):
    retuser = make_user(user['name'], user['username'])
    for submission in user['submissions']:
        # judgement, problem, time
        judgement = submission['judgement']
        if 'accepted' in judgement.lower():
            problem = submission['problem']
            time = submission['time']
            sub = make_submission(time=time, problemid=problem, problemname=problem,
                                  user=retuser.name)
            user_add_submission(retuser, sub)
    return retuser

def get_sessions_by(sessions, pred, name):
    return [(sessions[session][name], session) for session in filter(pred, sessions)]


def count_for_all(fname):
    with open(fname, 'r') as f:
        contents = json.load(f)
    sessions = {S['name']: count_session_data(S) for S in contents['sessions']}
    users = {U['name']: count_user_data(U) for U in contents['students']}
    def is_individual(session):
        return '2' in session[-2:] or '3' in session[-2:] \
            or '5' in session[-2:] or '6' in session[-2:]
    def is_group(session):
        return '4' in session[-2:] or '7' in session[-2:]
    # print(get_sessions_by(sessions, is_individual, 'gustav-gransbo'))
    # print(get_sessions_by(sessions, is_group, 'gustav-gransbo'))
    for key in sorted(users):
        user = users[key]
        print('*'*42)
        print('* {} *'.format(user.name.ljust(38)))
        print('*'*42)
        count_points(user.submissions)
        print('* {} *'.format('Individual Sessions'.center(25)))
        my_sessions = reversed(sorted(get_sessions_by(sessions, is_individual, user.id)))
        for session in my_sessions:
            if session[0] > 0:
                print('   In {} {} got {} pts '.format(session[1], user.name, session[0]))
        print('* {} *'.format('Group Sessions'.center(25)))
        my_sessions = reversed(sorted(get_sessions_by(sessions, is_group, user.id)))
        for session in my_sessions:
            if session[0] > 0:
                print('   In {} {} got {} pts '.format(session[1], user.name, session[0]))

def main():
    if len(sys.argv) == 3 and sys.argv[1].lower() == 'students':
        fname = sys.argv[2]
        count_for_all(fname)
    else:
        count_for_me()


if __name__ == '__main__':
    main()
