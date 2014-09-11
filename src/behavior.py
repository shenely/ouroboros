#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 September 2014

TBD.

Classes:
BehaviorObject    -- TBD
PrimitiveBehavior -- TBD
CompositeBehavior -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision
2014-04-23    shenely         1.1         Finally figured out what to
                                            call this
2014-05-01    shenely         1.2         Removed ability to call
                                            execute composites, cleaned
                                            data update
2014-05-06    shenely         1.3         Moving away from getattr and
                                            setattr
2014-06-10    shenely         1.4         In composites, getattr and
                                            setattr were still being
                                            called
2014-06-11    shenely                     Added documentation
2014-08-18    shenely         1.5         Making all attributes private
                                            (ish)
2014-08-22    shenely         1.6         Combined behavior and structure
2014-09-10    shenely         1.7         Simpled data synchronization
"""


##################
# Import section #
#
#Built-in libraries
import types
import logging
import pickle
import copy

#External libraries
from bson import json_util
from networkx import DiGraph

#Internal libraries
from common import *
#
##################=


##################
# Export section #
#
__all__ = ["behavior",
           "required",
           "provided",
           "BehaviorObject",
           "PrimitiveBehavior",
           "CompositeBehavior"]
#
##################


####################
# Constant section #
#
__version__ = "1.7"#current version [major.minor]
#
####################


def behavior(**kwargs):
    def decorator(cls):
        cls._doc = ObjectDict(**copy.deepcopy(cls._doc)) \
                   if hasattr(cls,"_doc") \
                   else ObjectDict()
        
        cls._doc.name = cls.__name__
        #cls._doc.path = pickle.dumps(cls)
        
        cls._doc.story = cls._doc.story \
                         if hasattr(cls._doc,"story") else \
                         ObjectDict()
        cls._doc.story.update(kwargs)
        
        cls._doc.nodes = [ObjectDict(**node) for node in cls._doc.nodes] \
                         if hasattr(cls._doc,"nodes") else \
                         list()
                         
        cls._doc.links = []
        
        cls._doc.pins = [ObjectDict(**pin) for pin in cls._doc.pins] \
                         if hasattr(cls._doc,"pins") else \
                         list()
                         
        cls._doc.rules = []
        
        cls._checks = copy.deepcopy(cls._checks) \
                     if hasattr(cls,"_checks") \
                     else dict()
        
        return cls
    
    return decorator

def required(name,type,*checks):
    assert isinstance(name,types.StringTypes)
    assert issubclass(type,BehaviorObject)
    
    def decorator(cls):
        assert issubclass(cls,BehaviorObject)
        
        for node in cls._doc.nodes:
            if node.name == name:
                node.type = type.__name__
                
                break
        else:
            cls._doc.nodes.append(ObjectDict(name=name,
                                             type=type.__name__,
                                             pins=[]))
                
        for pin in cls._doc.pins:
            if pin.node == name:
                pin.type = "required"
                
                break
        else:
            cls._doc.pins.append(ObjectDict(node=name,
                                            type="required"))
            
        cls._checks[name] = checks
        
        return cls
    
    return decorator

def provided(name,type,*checks):
    assert isinstance(name,types.StringTypes)
    assert issubclass(type,BehaviorObject)
    
    def decorator(cls):
        assert issubclass(cls,BehaviorObject)
        
        for node in cls._doc.nodes:
            if node.name == name:
                node.type = type.__name__
                
                break
        else:
            cls._doc.nodes.append(ObjectDict(name=name,
                                             type=type.__name__,
                                             pins=[]))
                
        for pin in cls._doc.pins:
            if pin.node == name:
                pin.type = "provided"
                
                break
        else:
            cls._doc.pins.append(ObjectDict(node=name,
                                            type="provided"))
            
        cls._checks[name] = checks
        
        return cls
    
    return decorator

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    @classmethod
    def install(cls,service):
        cls._doc.path = pickle.dumps(cls)
        
        service.set(cls._doc)
    
    def __init__(self,name,pins,data=DiGraph(),control=DiGraph(),graph=None):
        super(BehaviorObject,self).__init__()
        
        self._name = name
        
        self._data = data# data flow
        self._control = control# control flow
        self._super = graph# control flow (of parent)
        
        #Initialize data values
        for pin in pins:
            setattr(self,pin.name,pin.value)
    
    def __call__(self,graph):
        """Execute behavior in a context."""
        raise NotImplemented
            
    def __getattr__(self,name):
        """"Get value of a provided interface."""
        try:
            data = super(BehaviorObject,self).__getattr__("_data")\
                   .node.get((name,None))
            
            #Can only get provided interfaces
            if data is None:
                #TODO:  Provided interface warning (shenely, 2014-06-10)
                #raise Warning# does not exist
            
                value = super(BehaviorObject,self).__getattr__(name)
            else:
                if data.get("type") != "provided":
                    pass#raise Warning# is not provided
                
                value = data.get("node")
                
                if isinstance(value,BehaviorObject):pass
                    #assert isinstance(value,data.get("cls")) or issubclass(value.__class__,data.get("cls"))
                else:
                    value = data.get("cls")(name,[ObjectDict(value=value)])
                    
                [check(self,value) for check in self._checks[name]]
        except AttributeError:
            value = super(BehaviorObject,self).__getattr__(name)
            
        return value
            
    def __setattr__(self,name,value):
        """Set value of required interface."""
        try:
            data = super(BehaviorObject,self).__getattr__("_data")\
                   .node.get((name,None))
            control = super(BehaviorObject,self).__getattr__("_control")\
                      .node.get(name)
            
            #Can only set required interfaces
            if data is None or control is None:
                #TODO:  Required interface warning (shenely, 2014-06-10)
                #raise Warning# does not exist
            
                super(BehaviorObject,self).__setattr__(name,value)
            else:
                if data.get("type") != "required":
                    pass#raise Warning# is not required
                
                if isinstance(value,BehaviorObject):
                    assert isinstance(value,data.get("cls"))
                else:
                    value = data.get("cls")(name,[ObjectDict(name="value",value=value)])
                    
                [check(self,value) for check in self._checks[name]]
    
                data["node"] = value
                control["node"] = value
        except AttributeError:
            super(BehaviorObject,self).__setattr__(name,value)

@behavior()
class PrimitiveBehavior(BehaviorObject):
    """Primitive (simple) behavior"""
    
    def __init__(self,*args,**kwargs):
        super(PrimitiveBehavior,self).__init__(*args,**kwargs)
                       
        logging.debug("{0}:  Starting".\
                      format(self._name))
        
    def __del__(self):
        logging.warn("{0}:  Stopping".\
                     format(self._name))
    
    def __call__(self):
        logging.debug("{0}:  Processing".\
                     format(self._name))
        
        mode = self._process()

        logging.debug("{0}:  Processed".\
                     format(self._name))
        
        return mode
        
    def default(self,obj):
        obj = json_util.default(obj)
            
        return obj
        
    def object_hook(self,dct):
        dct = json_util.object_hook(dct)
    
        return dct
    
    def _process(self):
        raise NotImplemented

@behavior()
class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""