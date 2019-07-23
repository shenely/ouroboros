# built-in libraries
import functools
import time
import datetime
import logging

# external libraries
# ...

# internal libraries
from ouroboros.conf import ISO_8601, UNIX_EPOCH, STONE

# exports
__all__ = ("coroutine",
           "default", "object_hook",
           "parse_time", "parse_rate")

# constants
# ...

# logging
logger = logging.getLogger(__name__)


def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


def default(obj):
    """Return a serializable version of `object`"""
    try:
        return next({key: type.default(obj)}
                    for ((key, cls), type)
                    in STONE.items()
                    if isinstance(obj, cls))
    except StopIteration:
        raise TypeError


def object_hook(dct):
    """Return value instead of the `dict`"""
    return next((type.object_hook(dct)
                 for ((key, cls), type)
                 in STONE.items()
                 if key in dct), dct)


def parse_time(s):
    assert isinstance(s, str)
    if s.lower() == "now":
        t = time.time()
    elif s.isdigit():
        t = int(s)
    else:
        dt = datetime.datetime.strptime(s, ISO_8601)
        t = (dt - UNIX_EPOCH).total_seconds()
    return t


def parse_rate(s):
    assert isinstance(s, str)
    if s.lower() in "rt":
        x = 1.0
    else:
        x = float(s)
        assert x >= 0.0
    return x
