import copy
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
        return result_get_goal_points(self.result, goal)


def make_context():
    context = Context()
    add_builtin_functions(context)
    return context


def context_add_handler(context, handler):
    context.function_handlers.append(handler)


def context_set_result(context, result):
    context.result = result


def context_add_plugin(context, checker, resolver):
    # Plugins have priority over built-in functions
    context.function_handlers.appendleft((checker, resolver))

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
    def count_operand(values):
        return sum(map(bool, values))

    reducer_functions = [
        ('+', operator.add),
        ('-', operator.sub),
        ('*', operator.mul),
        ('/', operator.truediv),
    ]
    numeric_iterable_functions = [
        ('MAX', max),
        ('MIN', min),
        ('COUNT', count_operand)
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
        util.starmap_now(adder, provided_functions)

    context_add_handler(context, make_get_handler())
    util.starmap_now(add_handler, handler_makers)
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


def result_get_goal_points(result, goal_id):
    def is_correct_goal(goal):
        return goal.id == goal_id
    goal = util.find(is_correct_goal, result.goals)
    on_fail = lambda: 0
    on_success = lambda: goal.points
    return util.crossroad(lambda: goal, on_success, on_fail)


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
# Topological Sort                       #
##########################################


def find_expressions(expr, root):
    result = []

    def is_correct_expression(tree):
        return isinstance(tree, dict) and expr in tree
    def is_expression(tree):
        return isinstance(tree, dict)
    def is_list(tree):
        return isinstance(tree, list)

    def add_expression(tree):
        result.append(copy.deepcopy(tree))
    def find_in_children(tree):
        return find_expression_rec(list(tree.values()))
    def search_in_list(seq):
        return util.map_now(find_expression_rec, seq)

    def find_expression_rec(tree):
        util.cond([
            (is_correct_expression, util.combine(add_expression, find_in_children)),
            (is_expression, find_in_children),
            (is_list, search_in_list)
        ])(tree)

    find_expression_rec(root)
    return result

def topological_order(rules):
    # 1. Find each rule and the goals that it depends on
    # 2. Create a dependency tree where each rule depends
    #    on all rules that go towards what they depend on
    # 3. Solve dependency with toposort

    goal_dependencies = collections.defaultdict(set)
    def find_and_add_goals(index, rule):
        get_need = find_expressions('get', rule.needs)
        get_point = find_expressions('get', rule.points)
        all_goals = get_need + get_point
        add_goal = lambda expr: goal_dependencies[index].add(expr['get'])
        util.map_now(add_goal, all_goals)

    util.starmap_now(find_and_add_goals, enumerate(rules))


    def is_dependency_rule(index, original_idx):
        return rules[index].towards in goal_dependencies[original_idx]
    def find_rule_dependency(index):
        indices = range(len(rules))
        # Note: also include self, because we can have the case that a user writes
        # a rule that depends on itself being completed...
        indexes_to_add = filter(lambda idx: is_dependency_rule(idx, index), indices)
        return list(indexes_to_add)

    rule_dependency = util.map_now(find_rule_dependency, range(len(rules)))
    rule_rev_dependency = [[] for _ in range(len(rules))]
    def add_rev_dependency(key, values):
        util.map_now(lambda val: rule_rev_dependency[val].append(key), values)
    util.starmap_now(add_rev_dependency, enumerate(rule_dependency))
    connection_count = [len(x) for x in rule_dependency]

    # rule_rev_dependency is our dependency mapping and connection_count count
    # how many unsolved we depend on

    def should_add_to_queue(index):
        return connection_count[index] == 0
    def add_to_queue(index):
        queue.append(index)
    def process_item(index):
        connection_count[index] -= 1
        util.cond([
            (should_add_to_queue, add_to_queue)
        ])(index)
    queue = list(filter(should_add_to_queue, range(len(rules))))

    idx = 0
    # We need to continuously evaluate the length of the queue so we
    # need to run with a while loop -.-
    while idx < len(queue):
        item = queue[idx]
        util.map_now(process_item, rule_rev_dependency[item])
        idx += 1

    return queue


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
        points = 0
        try:
            points = context.value_expression(rule.points)
        except TypeError as e:
            print('Got a TypeError saying "{}"'.format(e))
            print('while trying to resolve points for: \n\n{}\n'.format(rule))
        result_update_resolved_goal(result, rule, points)

    def process_rule(rule):
        needs = context.bool_expression(rule.needs)
        success = lambda: on_rule_success(rule)
        fail = lambda: on_rule_fail(rule)
        util.crossroad(lambda: needs, success, fail)

    def process_by_index(index):
        process_rule(rules[index])

    order = topological_order(rules)
    util.map_now(process_by_index, order)
    return result
