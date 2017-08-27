"""This program was created in order to help the students and teachers
of TDDD95 at Linköping University. It is a tool with which students
can review how far they have come in the course and easily see what
they need to do in order to reach their desired grade. It is also a
tool for the teachers to get a good overview of how students are
doing as well as a tool used to help grade students.

The tool uses the submit script from Kattis, which basically allows
users to download any information from the kattis website accessible
to the user during "normal" login. (such as submission statistics).

In creating this tool I want to thank Fredrik Heintz and Tommy
Färnqvist for creating the TDDD95 course. I want to thank the people
at Kattis that do a good job at managing and running the kattis online
judge system. Lastly I want to thank all the students that have
previously attended the TDDD95 course and joked that they would need
to create a program just to understand how the grading works, which
spawned this idea.

"""
import aaps
import resolver
import rules
import util

import argparse
import collections
import colored


def as_color(string, color):
    return '{}{}{}'.format(colored.fg(color), string, colored.attr('reset'))

as_red = lambda string: as_color(string, 'red')
as_green = lambda string: as_color(string, 'green')
as_pink = lambda string: as_color(string, 'hot_pink_3a')
as_blue = lambda string: as_color(string, 'blue')
as_purple = lambda string: as_color(string, 'purple_1b')

Cross = '✗'
Check = '✓'

cross = as_red(Cross)
check = as_green(Check)

StudentResult = collections.namedtuple('StudentResult', 'student ruleset kattis context result')


def make_student_result(student, ruleset, kattis, context, result):
    return StudentResult(student, ruleset, kattis, context, result)


def print_student_result(student_result, detailed):
    student, ruleset, kattis, context, result = student_result
    print()
    print()
    print(student.name)
    print('-' * 42)
    print()

    def get_problem_id(problem):
        return util.crossroad(lambda: isinstance(problem, str),
                              lambda: problem,
                              lambda: problem['id'])

    def get_problem_points(problem):
        return util.crossroad(lambda: isinstance(problem, str),
                              lambda: 1,
                              lambda: problem['points'])

    def get_status_row(problem_id, points, deadline):
        no_subs = len(kattis.attempts_for(problem_id)) == 0
        if no_subs:
            return '[ - ]'
        AC = len(kattis.solutions_for(problem_id)) > 0
        WA_3 = len(kattis.WA_for(problem_id)) >= 3
        before_deadline = kattis.solved_before(problem_id, deadline)
        C = lambda b: util.cond([(lambda: b, lambda: check), (lambda: not b, lambda: cross)])()

        if not AC:
            points = 0
        if not before_deadline:
            points /= 2.0

        pts = as_green(points) if points > 0 else as_red(int(points))
        a = '{:16}'.format(pts)
        b = '{}'.format(C(AC))
        c = '{}'.format(C(WA_3))
        d = '{}'.format(C(before_deadline))

        message = '[ Pts? {}  AC? {}  +3WA? {}  Before Deadline? {} ]'
        return message.format(a, b, c, d)

    def print_problem_detail(idx, problem, deadline):
        indent = '   '
        if idx % 4 == 0 and idx > 0:
            print('{}  {}'.format(indent, as_pink('---')))

        problem_id = get_problem_id(problem)
        points = get_problem_points(problem)
        status_row = get_status_row(problem_id, points, deadline)
        print('{} {:46} {}'.format(indent, as_blue(problem_id) + ':', status_row))

    def print_uppgift_details(rule):
        problems = rule.points['uppgift']['problems']
        if 'deadline' in rule.points['uppgift']:
            deadline = rule.points['uppgift']['deadline']
        else:
            deadline = '01-01-2117 08:00'
        print_detail = lambda idx, problem: print_problem_detail(idx, problem, deadline)
        util.starmap_now(print_detail, enumerate(problems))

    def is_uppgift(rule):
        return isinstance(rule.points, dict) and 'uppgift' in rule.points

    def print_rule_resolution(rule, points):
        indent = '   '
        rule_name = as_purple(rule.name or 'Unnamed Rule')
        print('{}Rule: "{}" gave {} pts'.format(indent, rule_name, as_green(points)))
        util.cond([
            (is_uppgift, print_uppgift_details)
        ])(rule)

    def print_goal_resolutions(goal):
        util.starmap_now(print_rule_resolution, goal.resolved_rules)

    def print_goal(idx, goal, detailed):
        if idx % 4 == 0 and idx > 0:
            print('   {}'.format(as_pink('---')))
        name = '{:50}'.format(as_purple(goal.name))
        p = goal.points
        if int(p) == goal.points:
            p = int(p)
        points = '{:3}'.format(as_green(p))
        print(name, points)
        if detailed:
            print_goal_resolutions(goal)
    is_upg1 = lambda goal: goal.name.startswith('UPG1')
    is_lab1 = lambda goal: goal.name.startswith('LAB1')
    is_individual = lambda goal: goal.name.startswith('individual-session')
    is_group = lambda goal: goal.name.startswith('group-session')
    upg1_goals = util.filter_now(is_upg1, result.goals)
    lab1_goals = util.filter_now(is_lab1, result.goals)
    individual_goals = util.filter_now(is_individual, result.goals)
    group_goals = util.filter_now(is_group, result.goals)

    def print_goals(name, goals, detailed):
        print('Goals for {}'.format(as_red(name)))
        print(' {}'.format(as_pink('-------')))
        print_g = lambda idx, goal: print_goal(idx, goal, detailed)
        util.starmap_now(print_g, enumerate(goals))
        print(' {}'.format(as_pink('-------')))
        print()

    all_goals = [
        ('Individual Sessions', individual_goals, False),
        ('Group Sessions', group_goals, False),
        ('UPG1', upg1_goals, True),
        ('LAB1', lab1_goals, True)
    ]
    util.starmap_now(print_goals, all_goals)

    def get_id(goal):
        return goal.id

    def is_rest(goal):
        return goal.id not in map(get_id, upg1_goals) and \
            goal.id not in map(get_id, lab1_goals) and \
            goal.id not in map(get_id, individual_goals) and \
            goal.id not in map(get_id, group_goals)

    rest_goals = util.filter_now(is_rest, result.goals)
    #print_goals('Internal', rest_goals)

def main(rulepath, datapath, detailed=False, name_filter=None, is_student=False):
    ruleset = rules.parse_file(rulepath)
    exported = aaps.read_exported_kattis_file(datapath)

    def handle_student(student):
        kattis = aaps.KattisResult()
        if is_student:
            kattis.resolve_sessions_with_input()
        add_sub = lambda sub: kattis.add_submission(sub)
        util.map_now(add_sub, student.submissions)
        context = resolver.make_context()
        plugins = kattis.get_plugins()
        add_plugin = lambda c, r: resolver.context_add_plugin(context, c, r)
        util.starmap_now(add_plugin, plugins)
        result = resolver.resolve(ruleset, context)
        return make_student_result(student, ruleset, kattis, context, result)

    def name_match(student):
        return name_filter.lower() in student.name or \
            name_filter.lower() in student.username

    students = util.filter_now(name_match, exported.students)
    student_results = util.map_now(handle_student, students)

    print_result = lambda result: print_student_result(result, detailed)
    util.map_now(print_result, student_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kattis TDDD95')

    def add_flag(flag, help):
        parser.add_argument(flag, action='store_const', const=True, default=False, help=help)

    add_flag('--student', 'For viewing only your own results')
    add_flag('--detailed', 'For viewing detailed results')
    parser.add_argument('--data', help='Data to read from')
    parser.add_argument('--rules', help='Rules to use for judging')
    parser.add_argument('--filter', default='', help='Filter on name')
    args = parser.parse_args()
    main(args.rules, args.data, detailed=args.detailed, name_filter=args.filter,
         is_student=args.student)
