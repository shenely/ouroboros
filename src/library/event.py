#!/usr/bin/env python2.7

"""Event behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 September 2014

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-12    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta

#External libraries
from zmq.eventloop import ioloop

#Internal libraries
from behavior import PrimitiveBehavior
#
##################


##################
# Export section #
#
__all__ = ["EventPrimitive",
           "PeriodicEvent",
           "DelayedEvent",
           "HandlerEvent"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running
#
####################


class EventPrimitive(PrimitiveBehavior):
    
    def _callback(self):
        raise NotImplemented

class PeriodicEvent(EventPrimitive):
    
    def __init__(self,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        
        assert isinstance(self._timeout,timedelta)
        
        super(PeriodicEvent,self).__init__(*args,**kwargs)
    
    def event(self,app):
        def caller():
            app._process._loop.add_timeout(self._timeout,callback)
            
        def callback():
            app._process.schedule(self._super,self._name)
            
            app._process._loop.add_callback(caller)
        
        app._process._loop.add_callback(caller)

class DelayedEvent(EventPrimitive):
    
    def __init__(self,timeout=TIMEOUT,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        
        assert isinstance(self._timeout,timedelta)
        
        super(PeriodicEvent,self).__init__(*args,**kwargs)
    
    def event(self,app):
        def callback():
            app._process.schedule(self._super,self._name)
            
        app._process._loop.add_timeout(self._timeout,callback)

class HandlerEvent(EventPrimitive):
    
    @property
    def handle(self):
        raise NotImplemented
    
    def event(self,app):
        def callback():
            app._process.schedule(self._super,self._name)
            
        app._process._loop.add_handler(self.handle.value,callback,ioloop.POLLIN)