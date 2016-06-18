import json
import types
import functools
<<<<<<< HEAD
import datetime

import numpy
import bson.json_util

__all__ = ["coroutine",
           "Memoize",
           "Go", "All", "Many", "One", "No",
           "dumps", "loads"]

#Unit vectors
O = numpy.array([0,0,0])
I = numpy.array([1,0,0])
J = numpy.array([0,1,0])
K = numpy.array([0,0,1])

def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

class Memoize(type):
    def __init__(self, *args, **kwargs):
        super(Memoize, self).__init__(*args, **kwargs)
        self._cache = {}
    
    def __len__(self):
        return len(self._cache)
    
    def __getitem__(self, key):
        return self._cache[key]
    
    def __setitem__(self, key, value):
        self._cache[key] = value
    
    def __delitem__(self, key):
        del self._cache[key]
        
    def __iter__(self):
        return iter(self._cache)

class Go(Exception):pass

class All(Go):pass

class Many(Go):

    def __init__(self, *outs):
        self.value = outs

class One(Go):

    def __init__(self, out):
        self.value = out

class No(Go):pass

def object_hook(dct):
    dct = bson.json_util.object_hook(dct)

    if isinstance(dct, types.DictType):
        if "$tuple" in dct:
            dct = tuple(dct["$tuple"])
        elif "$elapse" in dct:
            dct = datetime.timedelta(seconds=dct["$elapse"])
        elif "$array" in dct:
            dct = numpy.array(dct["$array"])

    return dct

def default(obj):
    if isinstance(obj, types.TupleType):
        obj = { "$tuple": list(obj) }
    elif isinstance(obj, datetime.timedelta):
        obj = { "$elapse": obj.total_seconds() }
    elif isinstance(obj, numpy.ndarray):
        obj = { "$array": obj.tolist() }
    else:
        obj = bson.json_util.default(obj)
=======
from datetime import timedelta

from bson import json_util
from numpy import ndarray, array

__all__ = ["coroutine",
           "Go", "All", "Many", "One", "No",
           "dumps", "loads"]

#Unit vectors
O = array([0,0,0])
I = array([1,0,0])
J = array([0,1,0])
K = array([0,0,1])

def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

class Go(Exception):pass

class All(Go):pass

class Many(Go):

    def __init__(self, *outs):
        self.value = outs

class One(Go):

    def __init__(self, out):
        self.value = out

class No(Go):pass

def object_hook(dct):
    dct = json_util.object_hook(dct)

    if isinstance(dct, types.DictType):
        if "$elapse" in dct:
            dct = timedelta(dct["$elapse"])
        elif "$array" in dct:
            dct = array(dct["$array"])

    return dct

def default(obj):
    if isinstance(obj, timedelta):
        obj = { "$elapse": obj.total_seconds() }
    elif isinstance(obj, ndarray):
        obj = { "$array": obj.tolist() }
    else:
        obj = json_util.default(obj)
>>>>>>> branch 'master' of https://github.com/shenely/ouroboros.git

    return obj

dumps = functools.partial(json.dumps, default=default)
loads = functools.partial(json.loads, object_hook=object_hook)