def map_now(function, *iterables):
    '''A map equivalent that applies directly.'''
    return list(map(function, *iterables))
