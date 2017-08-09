import collections
import util
import time
import json


Submission = collections.namedtuple('Submission', 'id time result')


def make_submission(id, time, result):
    return Submission(id, time, result)


def make_solved_handler(kattis):
    def checker(context, tree):
        return isinstance(tree, dict) and 'solved' in tree
    def resolver(context, tree):
        return any(result.id == tree['solved'] for result in kattis.AC)
    return checker, resolver

def time_parse(timestr):
    # %d - day [01-31]
    # %m - month [01-12]
    # %Y - year [20XX]
    # %H - hour [00-23]
    # %M - minute [00-59]
    return time.strptime(timestr, '%d-%m-%Y %H:%M')

def time_compare(a, b):
    return time_parse(a) < time_parse(b)

def make_late_handler(kattis):
    def problem_solved(problem_id):
        return len(kattis.solutions_for(problem_id)) > 0

    def ac_before_deadline(problem_id, deadline):
        return problem_solved(problem_id) and \
            any(time_compare(solution.time, deadline)
                for solution in kattis.solutions_for(problem_id))

    def ac_after_deadline(problem_id, deadline):
        return problem_solved(problem_id) and \
            all(time_compare(deadline, solution.time)
                for solution in kattis.solutions_for(problem_id))

    def checker(context, tree):
        return isinstance(tree, dict) and 'late' in tree
    def resolver(context, tree):
        items = tree['late']
        before = context.value_expression(items['before'])
        after = context.value_expression(items['after'])
        deadline = items['deadline']
        problem_id = items['problem']
        return util.cond([
            (ac_before_deadline, util.constant(before)),
            (ac_after_deadline, util.constant(after)),
            (util.truthy, util.constant(0))
        ])(problem_id, deadline)

    return checker, resolver


def make_uppgift_handler(kattis):
    Problem = collections.namedtuple('Problem', 'id points')

    def is_string(e):
        return isinstance(e, str)
    def is_dict(e):
        return isinstance(e, dict)
    def problem_from_string(problem_id):
        return Problem(problem_id, 1)
    def problem_from_dict(obj):
        return Problem(obj['id'], obj['points'])
    make_problem = util.cond([
        (is_string, problem_from_string),
        (is_dict, problem_from_dict)
    ])

    def count_for_single_problem(problem, deadline):
        solutions = kattis.solutions_for(problem.id)
        problem_solved = len(solutions) > 0
        before_deadline = problem_solved and any(time_compare(s.time, deadline) for s in solutions)
        return (0.5 * problem_solved + 0.5 * before_deadline) * problem.points

    def checker(context, tree):
        return isinstance(tree, dict) and 'uppgift' in tree

    def resolver(context, tree):
        # If a problem does not have a deadline, then assume it is a lab
        # and move the deadline to something like 100 years from now.
        problems = util.map_now(make_problem, tree['uppgift']['problems'])
        deadline = tree['uppgift'].get('deadline', '01-01-2117 08:00')
        points = lambda problem: count_for_single_problem(problem, deadline)
        return sum(map(points, problems))

    return checker, resolver


def make_session_handler(kattis):
    def count_for_single_problem(problem, deadline):
        solutions = kattis.solutions_for(problem)
        problem_solved = len(solutions) > 0
        return 3 * problem_solved

    def checker(context, tree):
        return isinstance(tree, dict) and 'session' in tree

    def resolver(context, tree):
        deadline = tree['session']['end']
        problems = tree['session']['problems']
        points = lambda problem: count_for_single_problem(problem, deadline)
        return sum(map(points, problems))

    return checker, resolver


class KattisResult:

    def __init__(self):
        self.AC = []
        self.WA = []
        self.TLE = []
        self.MLE = []
        self.RTE = []

    def add_AC(self, id, time):
        self.AC.append(make_submission(id, time, 'AC'))

    def add_WA(self, id, time):
        self.WA.append(make_submission(id, time, 'WA'))

    def add_TLE(self, id, time):
        self.TLE.append(make_submission(id, time, 'TLE'))

    def add_MLE(self, id, time):
        self.MLE.append(make_submission(id, time, 'MLE'))

    def add_RTE(self, id, time):
        self.RTE.append(make_submission(id, time, 'RTE'))

    def add_submission(self, submission):
        array_choser = {
            'AC': self.AC,
            'WA': self.WA,
            'TLE': self.TLE,
            'MLE': self.MLE,
            'RTE': self.RTE
        }
        # Discard compile errors and judgements not listed
        array = array_choser.get(submission.result, [])
        array.append(submission)

    def solutions_for(self, problem_id):
        return util.filter_now(lambda s: s.id == problem_id, self.AC)

    def attempts_for(self, problem_id):
        same_id = lambda sub: sub.id == problem_id
        return util.filter_now(same_id, self.WA) + \
            util.filter_now(same_id, self.TLE) + \
            util.filter_now(same_id, self.MLE) + \
            util.filter_now(same_id, self.RTE)

    def get_plugins(self):
        return [
            make_solved_handler(self),
            make_late_handler(self),
            make_uppgift_handler(self),
            make_session_handler(self)
        ]


Student = collections.namedtuple('Student', 'username name email submissions')


def make_student(username, name, email=''):
    return Student(username, name, email, [])


def student_add_submission(student, submission):
    student.submissions.append(submission)


ExportedKattis = collections.namedtuple('ExportedKattisData', 'students')


def make_exported_kattis():
    return ExportedKattis([])


def exported_kattis_add_student(data, student):
    data.students.append(student)


def read_exported_kattis_file(fpath):
    with open(fpath, 'r') as fp:
        content = json.load(fp)
    json_students = content['students']

    def json_to_submission(submission):
        problem_id = submission['problem']
        judgement = submission['judgement']
        subtime = submission['time']
        judgement_translation_map = {
            'Wrong Answer': 'WA',
            'Time Limit Exceeded': 'TLE',
            'Accepted': 'AC',
            'Run Time Error': 'RTE',
            'Memory Limit Exceeded': 'MLE',
        }
        inputtimeformat = '%Y-%m-%d %H:%M:%S'
        time_struct = time.strptime(subtime, inputtimeformat)
        year, month, day, hour, minute = time_struct[:5]
        output_time = '{}-{}-{} {}:{}'.format(day, month, year, hour, minute)
        result = judgement_translation_map.get(judgement, '')
        return make_submission(problem_id, output_time, result)

    def json_to_student(root):
        username = root.get('username', '[No Username]')
        name = root.get('name', '[No Name]')
        email = root.get('email', '')
        json_submissions = root.get('submissions', [])
        submissions = util.map_now(json_to_submission, json_submissions)
        student = make_student(username, name, email)
        add_sub = lambda sub: student_add_submission(student, sub)
        util.map_now(add_sub, submissions)
        return student

    result = make_exported_kattis()
    students = util.map_now(json_to_student, json_students)
    add_student = lambda student: exported_kattis_add_student(result, student)
    util.map_now(add_student, students)

    def solve_time(starttime, solvetime):
        solvetime_in_s = solvetime * 60
        t = time.ctime(starttime + solvetime_in_s)
        year, month, day, hour, minute = t[:5]
        return '{}-{}-{} {}:{}'.format(day, month, year, hour, minute)

    def add_session_problem(student, problem, starttime):
        timestr = solve_time(starttime, problem['solve_time'])
        problem_id = problem['problem_name']
        submission = make_submission(problem_id, timestr, 'AC')
        student_add_submission(student, submission)

    def add_student_session_problems(starttime, student, problems):
        is_student = lambda s: s.username == student
        student_data = util.find(is_student, result.students)
        student_not_exist = util.constant(not bool(student_data))
        is_solved = lambda problem: 'solve_time' in problem
        add_problem = lambda problem: add_session_problem(student_data, problem, starttime)
        handle_single_problem = util.cond([
            (student_not_exist, util.noop),
            (is_solved, add_problem)
        ])
        util.map_now(handle_single_problem, problems)

    def add_team_result(starttime, result):
        members = result['members']
        problems = result['problems']
        add_for_student = lambda student: add_student_session_problems(starttime, student, problems)
        util.map_now(add_for_student, members)

    def add_session(session):
        # starttime in seconds since epoch
        starttime = int(session['starttime'])
        results = session['results']
        add_team = lambda result: add_team_result(starttime, result)
        util.map_now(add_team, results)

    util.map_now(add_session, content['sessions'])

    return result
