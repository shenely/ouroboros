#!/usr/bin/env python2.7

"""Common objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 September 2014

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
__all__ = ["ObjectDict",
           "BaseObject"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
#
####################


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
        
    def __deepcopy__(self,memo):
        result = self.__class__()
        memo[id(self)] = result
        
        for key,value in self.iteritems():
            setattr(result,key,copy.deepcopy(value,memo))
            
        return result

class BaseObject(ObjectDict):
    """Ouroboros base object"""