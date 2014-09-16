#!/usr/bin/env python2.7

"""Listening behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 September 2014

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-15    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
import logging

#External libraries
from zmq.eventloop import ioloop
import zmq

#Internal libraries
from behavior import PrimitiveBehavior
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
__version__ = "1.0"#current version [major.minor]

TIMEOUT = timedelta(0,1,0,0)#time between running
#
####################


class ListenerPrimitive(PrimitiveBehavior):
    
    def listen(self,app):
        raise NotImplemented

class PeriodicListener(ListenerPrimitive):
    
    def __init__(self,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        
        assert isinstance(self._timeout,timedelta)
        
        super(PeriodicListener,self).__init__(*args,**kwargs)
    
    def listen(self,app):        
        def caller():
            app._process._loop.add_timeout(self._timeout,callback)
            
        def callback():
            app._process.schedule(self._super,self._name)
            
            app._process._loop.add_callback(caller)
        
        app._process._loop.add_callback(caller)

class DelayedListener(ListenerPrimitive):
    
    def __init__(self,timeout=TIMEOUT,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        
        assert isinstance(self._timeout,timedelta)
        
        super(DelayedListener,self).__init__(*args,**kwargs)
    
    def listen(self,app):        
        def callback():
            app._process.schedule(self._super,self._name)
            
        app._process._loop.add_timeout(self._timeout,callback)

class HandlerListener(ListenerPrimitive):
    
    @property
    def handle(self):
        raise NotImplemented
    
    def listen(self,app):        
        def callback(handle,events):
            app._process.schedule(self._super,self._name)
            
        app._process._loop.add_handler(self.handle.value,callback,ioloop.POLLIN)