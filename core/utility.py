from functools import wraps


def empty(o):
    return len(o) == 0


def first(iterable):
    for i in iterable:
        return i


def as_(thing):
    def decorator(generator_func):
        @wraps(generator_func)
        def wrapped(*args, **kwargs):
            return thing(generator_func(*args, **kwargs))
        return wrapped
    return decorator
