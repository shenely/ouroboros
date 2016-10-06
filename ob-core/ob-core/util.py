import types
import json
import functools

__all__ = ["coroutine",
           "Memoize",
           "Go", "All", "Many", "One", "No",
           "register",
           "dumps", "loads"]

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

def register(type, key, object_hook, default):
    object_hooks[key] = object_hook
    defaults[key, type] = default
object_hooks = {}
defaults = {}

def object_hook(dct):
    for key in object_hooks:
        if key in dct:
            dct = object_hooks[key](dct[key])
            break
    
    return dct

def default(obj):
    for (key, type) in defaults:
        if isinstance(obj, type):
            obj = { key: defaults[key, type](obj) }
            break
    else:
        print obj
    
    return obj

dumps = functools.partial(json.dumps, default=default)
loads = functools.partial(json.loads, object_hook=object_hook)
        
register(types.TupleType, "$tuple",
         object_hook=lambda value: tuple(value),
         default=lambda obj: list(obj))