import itertools

def map_now(function, *iterables):
    '''A map equivalent that applies directly.'''
    return list(map(function, *iterables))

def crossroad(go_left, on_go_left, on_go_right):
    if go_left():
        return on_go_left()
    else:
        return on_go_right()

def noop():
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
    return find(lambda: True, values)
