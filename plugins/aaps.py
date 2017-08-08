import collections
import util
import time

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

    def add_AC(self, id, time):
        self.AC.append(make_submission(id, time, 'AC'))

    def add_WA(self, id, time):
        self.WA.append(make_submission(id, time, 'WA'))

    def solutions_for(self, problem_id):
        return util.filter_now(lambda s: s.id == problem_id, self.AC)

    def get_plugins(self):
        return [
            make_solved_handler(self),
            make_late_handler(self),
            make_uppgift_handler(self),
            make_session_handler(self)
        ]
