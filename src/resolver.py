import collections
import util
import functools
import operator


##########################################
# Context                                #
##########################################

class Context:

    def __init__(self):
        self.function_handlers = collections.deque()


    def value_expression(self, tree):
        pass


    def bool_expression(self, tree):
        pass


def make_context():
    context = Context()
    add_builtin_functions(context)
    return context


def context_add_handler(context, handler):
    context.function_handlers.append(handler)


##########################################
# Builtin functions for context          #
##########################################

def make_checker(string):
    def checker(context, tree):
        return string in tree
    return checker


def make_reducer(string, oper):
    def reducer(context, tree):
        expressions = tree[string]
        handle_expr = lambda expr: context.value_expression(expr)
        values = util.map_now(handle_expr, expressions)
        return functools.reduce(oper, values)
    return reducer


def make_comparison_resolver(string, oper):
    def resolver(context, tree):
        expression = tree[string]
        lhs, rhs = expression['lhs'], expression['rhs']
        handle_expr = lambda expr: context.value_expression(expr)
        lhs_value, rhs_value = util.map_now(handle_expr, [lhs, rhs])
        return oper(lhs_value, rhs_value)
    return resolver


def make_reduction_handler(string, oper):
    return (make_checker(string), make_reducer(string, oper))


def make_type_handler(target_type):
    checker = lambda context, tree: isinstance(tree, target_type)
    resolver = lambda context, tree: tree
    return (checker, resolver)


def make_comparison_handler(string, oper):
    return (make_checker(string), make_comparison_resolver(string, oper))


def add_builtin_functions(context):
    # Set up data for reducer functions
    reducer_functions = [
        ('+', operator.add),
        ('-', operator.sub),
        ('*', operator.mul),
        ('/', operator.truediv),
        ('MAX', max),
        ('MIN', min)
    ]
    def add_reduction_function(string, oper):
        context_add_handler(context, make_reduction_handler(string, oper))

    # Set up data for comparison functions
    comparison_functions = [
        ('<', operator.lt),
        ('<=', operator.le),
        ('=', operator.eq),
        ('!=', operator.ne),
        ('>=', operator.ge),
        ('>', operator.gt)
    ]
    def add_comparison_function(string, oper):
        context_add_handler(context, make_comparison_handler(string, oper))

    # Add comparison functions and type functions
    util.map_now(lambda val: add_reduction_function(*val), reducer_functions)
    util.map_now(lambda val: add_comparison_function(*val), comparison_functions)
    context_add_handler(context, make_type_handler(bool))
    context_add_handler(context, make_type_handler(int))


##########################################
# Result                                 #
##########################################


class Result:

    def __init__(self):
        self.goals = []


def result_get_goals(result):
    return result.goals


def result_add_goal(result, goal):
    result.goals.append(goal)


def result_get_or_add_goal(result, rule):

    def on_fail():
        goal = make_goal_from_rule(rule)
        result_add_goal(result, goal)
        return goal

    def is_correct_goal(goal):
        return rule.towards == goal.id

    def get_goal():
        goal = util.find(is_correct_goal, result_get_goals(result))
        return goal

    return util.crossroad(get_goal, get_goal, on_fail)


def result_update_resolved_goal(result, rule, points):
    goal = result_get_or_add_goal(result, rule)
    goal_add_points(goal, points)
    goal_add_resolved_rule(rule, points)


def result_update_failed_goal(result, rule):
    goal = result_get_or_add_goal(result, rule)
    goal_add_non_resolved_rule(goal, rule)


##########################################
# Goal                                   #
##########################################


class Goal:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.points = 0
        self.resolved_rules = []
        self.non_resolved_rules = []

    def __str__(self):
        return '<Goal id={} name={} points={}>'.format(self.id, self.name, self.points)

def make_goal(id, name):
    return Goal(id, name)


def make_goal_from_rule(rule):
    return make_goal(rule.towards, rule.towards)


def goal_add_points(goal, points):
    goal.points += points


def goal_add_resolved_rule(goal, rule, points):
    goal.resolved_rules.append((rule, points))


def goal_add_non_resolved_rule(goal, rule):
    goal.non_resolved_rules.append(rule)


##########################################
# Resolver function                      #
##########################################


def resolve(ruleset, context):
    rules = ruleset.rules
    result = Result()

    def on_rule_fail(rule):
        result_update_failed_goal(result, rule)
    def on_rule_success(rule):
        points = context.value_expression(rule.points)
        result_update_resolved_goal(result, rule, points)

    def process_rule(rule):
        needs = context.bool_expression(rule.needs)
        success = lambda: on_rule_success(rule)
        fail = lambda: on_rule_fail(rule)
        util.crossroad(lambda: needs, success, fail)

    util.map_now(process_rule, rules)
    print(result.goals[0])
    return result
