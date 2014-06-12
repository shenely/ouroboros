#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 June 2014

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
                                            setattr were still being called
2014-06-11    shenely                     Added documentation
"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries
from networkx import DiGraph

#Internal libraries
from common import coroutine,BaseObject
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
__version__ = "1.4"#current version [major.minor]
#
####################


class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    def __init__(self,name,pins,data=DiGraph(),control=DiGraph(),graph=None):
        super(BehaviorObject,self).__init__()
        
        self.name = name
        
        self.data = data# data flow
        self.control = control# control flow
        self.super = graph# control flow (of parent)
        
        #Initialize data values
        for pin in pins:
            self.set(pin.name,pin.value)
    
    def __call__(self,graph):
        """Execute behavior in a context."""
        raise NotImplemented
            
    def get(self,name):
        """"Get value of a provided interface."""
        data = self.data.node[(name,None)]
        
        #Can only get provided interfaces
        if data is None:
            #TODO:  Provided interface exception (shenely, 2014-06-10)
            raise Exception# does not exist
        elif data.get("type") != "provided":
            raise Exception# is not provided
        else:
            value = data.get("node")
            
            return value
            
    def set(self,name,value):
        """Set value of required interface."""
        data = self.data.node.get((name,None))
        control = self.control.node.get(name)
        
        #Can only set required interfaces
        if data is None or control is None:
            #TODO:  Required interface exception (shenely, 2014-06-10)
            raise Exception# does not exist
        elif data.get("type") != "required":
            raise Exception# is not required
        else:
            data["node"] = value
            control["node"] = value

class PrimitiveBehavior(BehaviorObject):
    """Primitive (simple) behavior"""
    
    def __init__(self,*args,**kwargs):
        super(PrimitiveBehavior,self).__init__(*args,**kwargs)
            
        self.routine = self._routine()
    
    def __call__(self):
        mode = self.routine.send()
        
        return mode
    
    @coroutine
    def _routine(self):
        mode = None
                       
        logging.debug("{0}:  Starting".\
                      format(self.name))
        while True:
            try:
                yield mode
            except GeneratorExit:
                logging.warn("{0}:  Stopping".\
                             format(self.name))
                
                return
            else:
                logging.debug("{0}:  Processing".\
                             format(self.name))
                
                mode = self._process()
        
                logging.debug("{0}:  Processed".\
                             format(self.name))
    
    def _process(self):
        raise NotImplemented

class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""
    
    def get(self,name):
        value = super(CompositeBehavior,self).get(name)
        
        self._update(value)
        
        return value
            
    def set(self,name,value):
        super(CompositeBehavior,self).set(name,value)
        
        self._update(value)
        
    def _update(self,value):
        """Update data in connected behaviors."""
        #NOTE:  Data flow update (shenely, 2014-06-11)
        # Iterates over each data node in the behavior.  For each
        #   successor, transfer the value from the behavior to the
        #   successor.  For each predecessor, transfer the value from
        #   the predecessor to the behavior.
        for source in value.data.node_iter(data=False):
            for target,data in self.data.successors_iter((self.name,
                                                          source[0]),
                                                         data=True):
                node = getattr(data,"node")
                
                node.set(target[1],value.get(source[0]))
                
            for target,data in self.data.predecessors_iter((self.name,
                                                            source[0]),
                                                           data=True):
                node = getattr(data,"node")
                
                value.set(source[0],node.get(target[1]))