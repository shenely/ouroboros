#!/usr/bin/env python2.7

"""Listening behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   30 June 2015

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-15    shenely         1.0         Initial revision
2014-10-15    shenely         1.1         Super is now behavior, not
                                            node
2015-04-20    shenely         1.2         Supporting new graph format
2015-06-04    shenely         1.3         Support handlers natively
2015-06-30    shenely         1.4         Removing unused dependencies

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries
from zmq.eventloop import ioloop
import simpy

#Internal libraries
from ouroboros.behavior import PrimitiveBehavior
#
##################


##################
# Export section #
#
__all__ = ["ListenerPrimitive",
           "PeriodicListener",
           "DelayedListener",
           "HandlerListener"]
#
##################


####################
# Constant section #
#
__version__ = "1.4"#current version [major.minor]
#
####################


class ListenerPrimitive(PrimitiveBehavior):
    
    def listen(self,app,graph,node):
        raise NotImplemented

class PeriodicListener(ListenerPrimitive):
    
    def __init__(self,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",1)
        self._callback = None
        
        assert isinstance(self._timeout,(types.IntType,
                                         types.FloatType))
        
        super(PeriodicListener,self).__init__(*args,**kwargs)
    
    def listen(self,app,thing,node):
        def callback():
            while True:
                yield app._process.schedule(thing,node)
                                
                yield app._process._env.timeout(self._timeout)
        
        app._process.listen(callback)

class DelayedListener(ListenerPrimitive):
    
    def __init__(self,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",1)
        self._callback = None
        
        assert isinstance(self._timeout,(types.IntType,
                                         types.FloatType))
        
        super(DelayedListener,self).__init__(*args,**kwargs)
    
    def listen(self,app,thing,node):
        def callback():
            yield app._process._env.timeout(self._timeout)
            
            yield app._process.schedule(thing,node)
            
        app._process.listen(callback)

class HandlerListener(ListenerPrimitive):
    
    @property
    def handle(self):
        raise NotImplemented
    
    def listen(self,app,thing,node):
        def callback():
            yield app._process._env.timeout(0)
            
            obj = thing._control_graph.node[node].get("obj")
            
            obj._caller()
        
            def handler(handle,events):
                app._process.schedule(thing,node)

            self._handler = app._process._loop.add_handler(obj.handle,handler,ioloop.POLLIN)
            
        app._process.listen(callback)
            
        