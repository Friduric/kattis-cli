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

import collections
import colored


def as_color(string, color):
    return '{}{}{}'.format(colored.fg(color), string, colored.attr('reset'))

as_red = lambda string: as_color(string, 'red')
as_green = lambda string: as_color(string, 'green')
as_pink = lambda string: as_color(string, 'hot_pink_3a')

StudentResult = collections.namedtuple('StudentResult', 'student ruleset kattis context result')


def make_student_result(student, ruleset, kattis, context, result):
    return StudentResult(student, ruleset, kattis, context, result)


def print_student_result(student_result):
    student, ruleset, kattis, context, result = student_result
    print()
    print()
    print(student.name)
    print('-' * 42)
    print()

    def print_goal(idx, goal):
        if idx % 4 == 0:
            print()
        name = '{:40}'.format(goal.name)
        p = goal.points
        if int(p) == goal.points:
            p = int(p)
        points = '{:3}'.format(as_green(p))
        print(name, points)
    is_upg1 = lambda goal: goal.name.startswith('UPG1')
    is_lab1 = lambda goal: goal.name.startswith('LAB1')
    is_individual = lambda goal: goal.name.startswith('individual-session')
    is_group = lambda goal: goal.name.startswith('group-session')
    upg1_goals = util.filter_now(is_upg1, result.goals)
    lab1_goals = util.filter_now(is_lab1, result.goals)
    individual_goals = util.filter_now(is_individual, result.goals)
    group_goals = util.filter_now(is_group, result.goals)

    def print_goals(name, goals):
        print('Goals for {}'.format(as_red(name)))
        util.starmap_now(print_goal, enumerate(goals))
        print()

    all_goals = [
        ('Individual Sessions', individual_goals),
        ('Group Sessions', group_goals),
        ('UPG1', upg1_goals),
        ('LAB1', lab1_goals)
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

def teacher_main():
    rulepath = 'rules/rules.json'
    exportedpath = 'data/AAPS-AAPS17_export_all.json'
    ruleset = rules.parse_file(rulepath)
    exported = aaps.read_exported_kattis_file(exportedpath)

    def handle_student(student):
        kattis = aaps.KattisResult()
        add_sub = lambda sub: kattis.add_submission(sub)
        util.map_now(add_sub, student.submissions)
        context = resolver.make_context()
        plugins = kattis.get_plugins()
        add_plugin = lambda c, r: resolver.context_add_plugin(context, c, r)
        util.starmap_now(add_plugin, plugins)
        result = resolver.resolve(ruleset, context)
        return make_student_result(student, ruleset, kattis, context, result)

    student_results = util.map_now(handle_student, exported.students)
    util.map_now(print_student_result, student_results)



if __name__ == '__main__':
    teacher_main()
