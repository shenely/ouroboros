#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 August 2014

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
"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries
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
__version__ = "1.6"#current version [major.minor]
#
####################


def behavior(**kwargs):
    def decorator(cls):
        cls._doc = ObjectDict(**cls._doc) \
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
        
        return cls
    
    return decorator

def required(name,type):
    assert isinstance(name,types.StringTypes)
    assert issubclass(type,BehaviorObject)
    
    def decorator(cls):
        assert issubclass(cls,BehaviorObject)
        
        meth = getattr(cls,name)
        
        assert isinstance(meth,types.UnboundMethodType)
        
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
        
        def func(self,value):
            assert isinstance(value,type)
            
            self.__setattr__(name,value)
            
            meth(self,value)
        
        setattr(cls,name,property(func,None))
        
        return cls
    
    return decorator

def provided(name,type):
    assert isinstance(name,types.StringTypes)
    assert issubclass(type,BehaviorObject)
    
    def decorator(cls):
        assert issubclass(cls,BehaviorObject)
        
        meth = getattr(cls,name)
        
        assert isinstance(meth,types.UnboundMethodType)
        
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
        
        def func(self):
            value = self.__getattr__(name)
            
            assert isinstance(value,type)
            
            meth(self,value)
            
            return value
        
        setattr(cls,name,property(func,None))
        
        return cls
    
    return decorator

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    def __init__(self,name,pins,data=DiGraph(),control=DiGraph(),graph=None):
        super(BehaviorObject,self).__init__()
        
        self._name = name
        
        self._data = data# data flow
        self._control = control# control flow
        self._super = graph# control flow (of parent)
        
        #Initialize data values
        for pin in pins:
            self.__setattr__(pin.name,pin.value)
    
    def __call__(self,graph):
        """Execute behavior in a context."""
        raise NotImplemented
            
    def __getattr__(self,name):
        """"Get value of a provided interface."""
        data = self._data.node[(name,None)]
        
        #Can only get provided interfaces
        if data is None:
            #TODO:  Provided interface warning (shenely, 2014-06-10)
            raise Warning# does not exist
        
            value = super(BehaviorObject,self).__getattr__(name)
        else:
            if data.get("type") != "provided":
                raise Warning# is not provided
            
            value = data.get("node")
            
        return value
            
    def __setattr__(self,name,value):
        """Set value of required interface."""
        data = self._data.node.get((name,None))
        control = self._control.node.get(name)
        
        #Can only set required interfaces
        if data is None or control is None:
            #TODO:  Required interface warning (shenely, 2014-06-10)
            raise Warning# does not exist
        
            super(BehaviorObject,self).__setattr__(name,value)
        else:
            if data.get("type") != "required":
                raise Warning# is not required

            data["node"] = value
            control["node"] = value

class PrimitiveBehavior(BehaviorObject):
    """Primitive (simple) behavior"""
    
    def __init__(self,*args,**kwargs):
        super(PrimitiveBehavior,self).__init__(*args,**kwargs)
                       
        logging.debug("{0}:  Starting".\
                      format(self.name))
        
    def __del__(self):
        logging.warn("{0}:  Stopping".\
                     format(self.name))
    
    def __call__(self):        
        logging.debug("{0}:  Processing".\
                     format(self.name))
        
        mode = self._process()

        logging.debug("{0}:  Processed".\
                     format(self.name))
        
        return mode
    
    def _process(self):
        raise NotImplemented

class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""
    
    def __getattr__(self,name):
        value = super(CompositeBehavior,self).__getattr__(name)
        
        self._update(value)
        
        return value
            
    def __setattr__(self,name,value):
        super(CompositeBehavior,self).__setattr__(name,value)
        
        self._update(value)
        
    def _update(self,value):
        """Update data in connected behaviors."""
        #NOTE:  Data flow update (shenely, 2014-06-11)
        # Iterates over each data node in the behavior.  For each
        #   successor, transfer the value from the behavior to the
        #   successor.  For each predecessor, transfer the value from
        #   the predecessor to the behavior.
        for source in value._data.node_iter(data=False):
            for target,data in self._data.successors_iter((self._name,
                                                           source[0]),
                                                          data=True):
                node = getattr(data,"node")
                
                setattr(node,target[1],getattr(value,source[0]))
                
            for target,data in self._data.predecessors_iter((self._name,
                                                             source[0]),
                                                            data=True):
                node = getattr(data,"node")
                
                setattr(value,source[0],getattr(node,target[1]))