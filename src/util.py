import collections
import itertools


def consume(iterator, n=None):
    # Taken from https://docs.python.org/3.3/library/itertools.html#itertools-recipes
    if n is None:
        collections.deque(iterator, maxlen=0)
    else:
        next(itertools.islice(iterator, n, n), None)


def map_now(function, *iterables):
    iterator = map(function, *iterables)
    return consume(iterator)
