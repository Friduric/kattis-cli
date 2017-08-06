import collections


class Context:

    def __init__(self):
        self.point_handler = None


def make_context():
    return Context()


def context_use_zero_resolver(context):
    pass


class Result:

    def __init__(self):
        self.goals = []

def resolve(ruleset, context):
    return Result()
