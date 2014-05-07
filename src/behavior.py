#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 May 2014

TBD.

Classes:
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
"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries
from network import DiGraph

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
__version__ = "1.3"#current version [major.minor]
#
####################


class BehaviorObject(BaseObject):
    def __init__(self,name,pins,data=DiGraph(),control=DiGraph(),parent=None):
        super(BehaviorObject,self).__init__()
        
        self.name = name
        
        self.data = data
        self.control = control
        self.parent = parent
        
        for pin in pins:
            self.set(pin.name,pin.value)
    
    def __call__(self,graph):
        raise NotImplemented
            
    def get(self,name):
        data = self.data.node[(name,None)]
        
        if data is None:
            raise Exception#does not exist
        elif data.get("type") != "provided":
            raise Exception#is not provided
        else:
            value = data.get("node")
            
            return value
            
    def set(self,name,value):
        data = self.data.node.get((name,None))
        control = self.control.node.get(name)
        
        if data is None or control is None:
            raise Exception#does not exist
        elif data.get("type") != "required":
            raise Exception#is not required
        else:
            data["node"] = value
            control["node"] = value

class PrimitiveBehavior(BehaviorObject):
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
                
    def get(self,name):
        value = super(CompositeBehavior,self).__getattr__(name)
        
        self._update(value)
        
        return value
            
    def set(self,name,value):
        super(CompositeBehavior,self).__setattr__(name,value)
        
        self._update(value)
        
    def _update(self,value):
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