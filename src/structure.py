#!/usr/bin/env python2.7

"""Structural decorators

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 August 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-22    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import types
import pickle

#External libraries

#Internal libraries
from common import ObjectDict
from behavior import BehaviorObject
#
##################=


##################
# Export section #
#
__all__ = ["behavior",
           "required",
           "provided"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################


def behavior(who,when,where,what,why):
    def decorator(cls):
        cls._doc = cls._doc if hasattr(cls._doc) else ObjectDict()
        
        cls._doc.name = cls.__name__
        cls._doc.path = pickle.dumps(cls)
        
        cls._doc.why = why
        cls._doc.when = when
        cls._doc.where = where
        cls._doc.what = what
        cls._doc.why = why
        
        cls._doc.nodes = []
        cls._doc.links = []
        cls._doc.pins = []
        cls._doc.rules = []
        
        return cls

def required(type):
    assert issubclass(type,BehaviorObject)
    
    def decorator(meth):
        assert isinstance(meth,types.UnboundMethodType)
        assert issubclass(meth.im_class,BehaviorObject)
        
        for node in meth.im_class._doc.nodes:
            if node.name == meth.__name__:
                node.type = type
                
                break
        else:
            meth.im_class._doc.nodes.append(ObjectDict(name=meth.__name__,
                                                       type=type,pins=[]))
                
        for pin in meth.im_class._doc.pins:
            if pin.name == meth.__name__:
                pin.type = type
                
                break
        else:
            meth.im_class._doc.pins.append(ObjectDict(node=meth.__name__,
                                                      type="required"))
        
        def func(self,value):
            assert isinstance(value,type)
            
            self.__setattr__(meth.__name__,value)
            
            meth(self,value)
        
        prop = property(func,None)
        
        return prop

def provided(type):
    assert issubclass(type,BehaviorObject)
    
    def decorator(meth):
        assert isinstance(meth,types.UnboundMethodType)
        assert issubclass(meth.im_class,BehaviorObject)
        
        for node in meth.im_class._doc.nodes:
            if node.name == meth.__name__:
                node.type = type
                
                break
        else:
            meth.im_class._doc.nodes.append(ObjectDict(name=meth.__name__,
                                                       type=type,pins=[]))
                
        for pin in meth.im_class._doc.pins:
            if pin.name == meth.__name__:
                pin.type = type
                
                break
        else:
            meth.im_class._doc.pins.append(ObjectDict(node=meth.__name__,
                                                      type="required"))
        
        def func(self):
            value = self.__getattr__(meth.__name__)
            
            assert isinstance(value,type)
            
            meth(self,value)
            
            return value
        
        prop = property(None,func)
        
        return prop