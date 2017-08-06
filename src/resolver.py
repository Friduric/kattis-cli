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
        self.result = None

    def handle_expression(self, tree):
        handler = util.cond(self.function_handlers)
        return handler(self, tree)


    def value_expression(self, tree):
        result = self.handle_expression(tree)
        # TODO: Do some checking that this is a value
        return result


    def bool_expression(self, tree):
        result = self.handle_expression(tree)
        # TODO: Do some checking that this is a boolean
        return result

    def get_goal_value(self, goal):
        return 0

def make_context():
    context = Context()
    add_builtin_functions(context)
    return context


def context_add_handler(context, handler):
    context.function_handlers.append(handler)


def context_set_result(context, result):
    context.result = result


##########################################
# Builtin functions for context          #
##########################################

def make_checker(string):
    def checker(context, tree):
        return isinstance(tree, dict) and string in tree
    return checker


def make_general_resolver(string, oper, get_values, handle_expr):
    def resolver(context, tree):
        expression = tree[string]
        values = util.map_now(lambda expr: handle_expr(context, expr), get_values(expression))
        return oper(values)
    return resolver


def make_general_handler(string, oper, get_values, handle_expr):
    return make_checker(string), make_general_resolver(string, oper, get_values, handle_expr)


def make_reduction_handler(string, oper):
    handle_expression = lambda context, expr: context.value_expression(expr)
    operand = lambda values: functools.reduce(oper, values)
    return make_general_handler(string, operand, util.identity, handle_expression)


def make_comparison_handler(string, oper):
    get_values = lambda expr: (expr['lhs'], expr['rhs'])
    handle_expr = lambda context, expr: context.value_expression(expr)
    operand = lambda values: oper(*values)
    return make_general_handler(string, operand, get_values, handle_expr)


def make_type_handler(target_type):
    checker = lambda context, tree: isinstance(tree, target_type)
    resolver = lambda context, tree: tree
    return (checker, resolver)


def make_numeric_iterable_handler(string, oper):
    handle_expression = lambda context, expr: context.value_expression(expr)
    return make_general_handler(string, oper, util.identity, handle_expression)


def make_bool_iterable_handler(string, oper):
    handle_expression = lambda context, expr: context.bool_expression(expr)
    return make_general_handler(string, oper, util.identity, handle_expression)


def make_numeric_handler(string, oper):
    handle_expression = lambda context, expr: context.value_expression(expr)
    operand = lambda values: oper(values[0])
    return make_general_handler(string, operand, util.list_wrap, handle_expression)


def make_get_handler():
    handle_expression = lambda context, expr: context.get_goal_value(expr)
    return make_general_handler('get', util.list_unwrap, util.list_wrap, handle_expression)


def add_builtin_functions(context):
    # Set up data for reducer functions
    reducer_functions = [
        ('+', operator.add),
        ('-', operator.sub),
        ('*', operator.mul),
        ('/', operator.truediv),
    ]
    numeric_iterable_functions = [
        ('MAX', max),
        ('MIN', min)
    ]
    bool_iterable_functions = [
        ('AND', all),
        ('OR', any)
    ]
    numeric_functions = [
        ('positive', lambda x: x > 0),
        ('negative', lambda x: x < 0),
        ('zero', lambda x: x == 0)
    ]
    comparison_functions = [
        ('<', operator.lt),
        ('<=', operator.le),
        ('=', operator.eq),
        ('!=', operator.ne),
        ('>=', operator.ge),
        ('>', operator.gt)
    ]
    handler_makers = [
        (make_reduction_handler, reducer_functions),
        (make_numeric_iterable_handler, numeric_iterable_functions),
        (make_bool_iterable_handler, bool_iterable_functions),
        (make_numeric_handler, numeric_functions),
        (make_comparison_handler, comparison_functions)
    ]

    def add_handler(handler, provided_functions):
        def adder(string, oper):
            context_add_handler(context, handler(string, oper))
        util.map_now(lambda values: adder(*values), provided_functions)

    context_add_handler(context, make_get_handler())
    util.map_now(lambda values: add_handler(*values), handler_makers)
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
    goal_add_resolved_rule(goal, rule, points)


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
    context_set_result(context, result)

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
    return result
