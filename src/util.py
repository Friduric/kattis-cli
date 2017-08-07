import itertools

def map_now(function, *iterables):
    '''A map equivalent that applies directly.'''
    return list(map(function, *iterables))

def starmap_now(function, iterable):
    return list(map(lambda value: function(*value), iterable))

def crossroad(go_left, on_go_left, on_go_right):
    if go_left():
        return on_go_left()
    else:
        return on_go_right()

def noop(*args, **kwargs):
    pass

def take(n, iterable):
    return list(itertools.islice(iterable, n))

def find(pred, iterable):
    result = take(1, filter(pred, iterable)) or [None]
    return result[0]

def cond(iterable):
    def handler(*args, **kwargs):
        for pred, handle in iterable:
            if pred(*args, **kwargs):
                return handle(*args, **kwargs)
    return handler

def identity(elem):
    return elem

def list_wrap(elem):
    return [elem]

def list_unwrap(values):
    return find(lambda x: True, values)

def combine(*functions):
    '''Combines several functions into one function.'''
    def inner(*args, **kwargs):
        return map_now(lambda func: func(*args, **kwargs), functions)
    return inner

def truthy(*args, **kwargs):
    return True

def falsy(*args, **kwargs):
    return False

def constant(value):
    def inner(*args, **kwargs):
        return value
    return inner
