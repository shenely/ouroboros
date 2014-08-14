#!/usr/bin/env python2.7

"""Common objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 June 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-05    shenely         1.0         Initial revision
2014-06-11    shenely                     Added documentation

"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = ["coroutine",
           "ObjectDict",
           "BaseObject"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


def coroutine(func):
    def wrapper(*args,**kw):
        gen = func(*args, **kw)
        gen.next()
        return gen
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    return wrapper


class ObjectDict(dict):
    """JSON-compatible object/dictionary"""
    
    def __getattr__(self,name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
    
    def __setattr__(self,name,value):
        self[name] = value
    
    def __delattr__(self,name):
        del self[name]

class BaseObject(ObjectDict):
    """Ouroboros base object"""