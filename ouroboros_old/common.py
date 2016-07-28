#!/usr/bin/env python2.7

"""Common objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-05    shenely         1.0         Initial revision
2014-06-11    shenely                     Added documentation
2014-08-18    shenely         1.1         Removed coroutine
2014-09-11    shenely         1.2         Added deep copy support
2015-02-08    shenely         1.3         Removing dict from inheritance
2016-06-18    shenely         1.4         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import copy

#External libraries

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = ["coroutine",
           "ObjectDict",
           "BaseObject",
           "Memoize"]
#
##################


####################
# Constant section #
#
__version__ = "1.4"#current version [major.minor]
#
####################


def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

class ObjectDict(dict):
    """JSON-compatible object/dictionary"""
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __delattr__(self, name):
        del self[name]
        
    def __deepcopy__(self, memo):
        result = self.__class__()
        memo[id(self)] = result
        
        for key,value in self.iteritems():
            setattr(result, key, copy.deepcopy(value, memo))
            
        return result

class BaseObject(object):
    """Ouroboros base object"""
    
class Memoize(type):
    """Memoize something"""
    
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