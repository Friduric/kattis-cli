import collections
import util

Submission = collections.namedtuple('Submission', 'id time result')


def make_submission(id, time, result):
    return Submission(id, time, result)


def make_solved_handler(kattis):
    def checker(context, tree):
        return isinstance(tree, dict) and 'solved' in tree
    def resolver(context, tree):
        return any(result.id == tree['solved'] for result in kattis.AC)
    return checker, resolver

def make_late_handler(kattis):
    def ac_before_deadline(problem_id, deadline):
        pass
    def ac_after_deadline(problem_id, deadline):
        pass
    def nil(problem_id, deadline):
        return 0

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
            (util.truthy, nil)
        ])(problem_id, deadline)

    return checker, resolver

class KattisResult:

    def __init__(self):
        self.AC = []
        self.WA = []

    def add_AC(self, id, time):
        self.AC.append(make_submission(id, time, 'AC'))

    def add_WA(self, id, time):
        self.WA.append(make_submission(id, time, 'WA'))

    def get_plugins(self):
        return [
            make_solved_handler(self),
            make_late_handler(self)
        ]
