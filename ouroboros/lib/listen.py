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
from datetime import timedelta
import logging

#External libraries

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

TIMEOUT = timedelta(seconds=1)#time between running
#
####################


class ListenerPrimitive(PrimitiveBehavior):
    
    def listen(self,app,graph,node):
        raise NotImplemented

class PeriodicListener(ListenerPrimitive):
    
    def __init__(self,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        self._callback = None
        
        assert isinstance(self._timeout,timedelta)
        
        super(PeriodicListener,self).__init__(*args,**kwargs)
    
    def listen(self,app,graph,node):
        if self._callback is not None:
            app._process._loop.remove_timeout(self._callback)
            
        def caller():
            self._callback = app._process._loop.add_timeout(self._timeout,callback)
            
        def callback():
            app._process.schedule(graph,node)
            
            app._process._loop.add_callback(caller)
        
        app._process._loop.add_callback(caller)

class DelayedListener(ListenerPrimitive):
    
    def __init__(self,timeout=TIMEOUT,*args,**kwargs):
        self._timeout = kwargs.pop("timeout",TIMEOUT)
        self._callback = None
        
        assert isinstance(self._timeout,timedelta)
        
        super(DelayedListener,self).__init__(*args,**kwargs)
    
    def listen(self,app,graph,node):
        if self._callback is not None:
            app._process._loop.remove_timeout(self._callback)
            
        def callback():            
            app._process.schedule(graph,node)
            
        self._callback = app._process._loop.add_timeout(self._timeout,callback)

class HandlerListener(ListenerPrimitive):
    
    @property
    def handle(self):
        raise NotImplemented
    
    def listen(self,app,graph,node):
        app._process.examine(graph,node)
            
        