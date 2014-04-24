#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   23 Apr 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision
2014-04-23    shenely         1.1         Finally figured out what to
                                            call this

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
from network import DiGraph

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = ["BehaviorObject",
           "PrimitiveBehavior",
           "CompositeBehavior"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class BaseObject(object):pass

class BehaviorObject(BaseObject):
    def __init__(self,name,pins,parent=None,data=DiGraph(),control=DiGraph()):
        super(BehaviorObject,self).__init__()
        
        self.name = name
        
        self.super = parent
        
        self.data = data
        self.control = control
        
        for pin in pins:
            setattr(self,pin.name,pin.value)
            
    def __getattr__(self,name):
        data = self.data.node[(name,None)]
        
        if data is None:
            raise Exception#does not exist
        elif data.get("type") != "provided":
            raise Exception#is not provided
        else:
            value = data.get("obj")
            
            return value
            
    def __setattr__(self,name,value):
        data = self.data.node.get((name,None))
        control = self.control.node.get(name)
        
        if data is None or control is None:
            raise Exception#does not exist
        elif data.get("type") != "required":
            raise Exception#is not required
        else:
            data["obj"] = value
            control["obj"] = value

class PrimitiveBehavior(BehaviorObject):pass

class CompositeBehavior(BehaviorObject):
    
    def __call__(self):
        for name,data in self.control.successors_iter(self.__class__.__name__,data=True):
            self.__class__.app.
                
    def __getattr__(self,name):
        value = super(CompositeBehavior,self).__getattr__(name)
        
        self._update(value)
        
        return value
            
    def __setattr__(self,name,value):
        super(CompositeBehavior,self).__setattr__(name,value)
        
        self._update(value)
        
    def _update(self,value):
        for source in value.data.node_iter(data=False):
            for target,data in self.data.successors_iter((self.name,source[0]),data=True):
                obj = data["obj"]
                
                try:
                    setattr(obj,target[1],getattr(value,source[0]))
                except:
                    try:
                        setattr(value,source[0],getattr(obj,target[1]))
                    except:
                        pass