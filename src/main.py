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


StudentResult = collections.namedtuple('StudentResult', 'student kattis context result')


def make_student_result(student, kattis, context, result):
    return StudentResult(student, kattis, context, result)


def print_student_result(student_result):
    student, kattis, context, result = student_result
    print('Information for: {}'.format(student.name))

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
        return make_student_result(student, kattis, context, result)

    student_results = util.map_now(handle_student, exported.students)
    util.map_now(print_student_result, student_results)



if __name__ == '__main__':
    teacher_main()
