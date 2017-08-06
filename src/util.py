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
    default = None
    return take(1, filter(pred, iterable)) or default

def cond(iterable):
    def handler(*args, **kwargs):
        for pred, handle in iterable:
            if pred(*args, **kwargs):
                return handle(*args, **kwargs)
    return handler
