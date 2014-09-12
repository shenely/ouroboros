#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 September 2014

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
2014-09-10    shenely         1.7         Simplified data synchronization
2014-09-11    shenely         1.8         Organized behavior decorators
"""


##################
# Import section #
#
#Built-in libraries
import types
import logging
import pickle
import copy
import warnings

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
__version__ = "1.8"#current version [major.minor]

DEFAULT_DOCUMENT = ObjectDict(\
    story=ObjectDict(
        who="me",
        when="now",
        where="here",
        what="that",
        why="because"),
    nodes=[],
    links=[],
    pins=[],
    rules=[])
#
####################


def inherit(cls):
    #NOTE:  Behavior inheritance (shenely, 2014-09-11)
    # All behaviors inherit provided and required interfaces as well as
    #   description stories.  The parent behavior's attributes are only
    #   inherited by the child once.  This is an optimization to
    #   minimize the amount of deep copies being executed.
    if hasattr(cls,"_doc"):
        if cls._doc.name != cls.__name__:
            cls._doc.name = cls.__name__
            
            cls._doc = copy.deepcopy(cls._doc)
        
            cls._checks = copy.deepcopy(cls._checks)
    else:
        cls._doc = copy.deepcopy(DEFAULT_DOCUMENT)
        cls._doc.name = cls.__name__
        cls._checks = dict()

def behavior(**kwargs):
    def decorator(cls):
        inherit(cls)
        
        cls._doc.story.update(kwargs)# child behavior's unique story
        
        return cls
    
    return decorator

def interface(mode,name,type,*checks):
    assert isinstance(name,types.StringTypes)
    assert issubclass(type,BehaviorObject)
    
    def decorator(cls):
        assert issubclass(cls,BehaviorObject)
        
        inherit(cls)
        
        #Check if there is an existing node
        for node in cls._doc.nodes:
            if node.name == name:
                node.type = type.__name__
                
                break
        else:
            #Add node if it doesn't exist
            cls._doc.nodes.append(ObjectDict(name=name,
                                             type=type.__name__,
                                             pins=[]))
        
        #Check if there is an existing pin
        for pin in cls._doc.pins:
            if pin.node == name:
                pin.type = mode# expose it if so
                
                break
        else:
            #Add pin if it doesn't exist
            cls._doc.pins.append(ObjectDict(node=name,
                                            type=mode))
            
        #XXX:  Interface checks (shenely, 2014-09-11)
        # Currently, all interface checks are done via functions
        #   (anonymous or otherwise).  This is only a temporary
        #   solution (that is working, by the way).  Ultimately, there
        #   should be a mechanism to identify and validate interfaces
        #   outside of the class definition.
        cls._checks[name] = checks# interface checks...
        
        return cls
    
    return decorator

def required(name,type,*checks):
    return interface("required",name,type,*checks)

def provided(name,type,*checks):
    return interface("provided",name,type,*checks)

@behavior()
class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    @classmethod
    def install(cls,service):
        inherit(cls)
        
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
                warnings.warn("does not exist",Warning)
            
                value = super(BehaviorObject,self).__getattr__(name)
            else:
                if data.get("type") != "provided":
                    warnings.warn("is not provided",Warning)
                
                value = data.get("node")
                
                if isinstance(value,BehaviorObject):
                    assert isinstance(value,data.get("cls")) or \
                           issubclass(value.__class__,data.get("cls"))
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
                warnings.warn("does not exist",Warning)
            
                super(BehaviorObject,self).__setattr__(name,value)
            else:
                if data.get("type") != "required":
                    warnings.warn("is not required",Warning)
                
                if isinstance(value,BehaviorObject):
                    assert isinstance(value,data.get("cls"))
                else:
                    value = data.get("cls")(name,[ObjectDict(name="value",
                                                             value=value)])
                
                #Check value of data
                [check(self,value) for check in self._checks[name]]
    
                data["node"] = value
                control["node"] = value
        except AttributeError:
            super(BehaviorObject,self).__setattr__(name,value)

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
        """For JSON encoder"""
        obj = json_util.default(obj)
            
        return obj
        
    def object_hook(self,dct):
        """For JSON decoder"""
        dct = json_util.object_hook(dct)
    
        return dct
    
    def _process(self):
        raise NotImplemented

class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""