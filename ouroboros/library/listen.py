#!/usr/bin/env python2.7

"""Listening behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

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
2015-07-24    shenely         1.5         Removed handler listener
2016-06-18    shenely         1.6         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries

#Internal libraries
from ..behavior import PrimitiveBehavior
#
##################


##################
# Export section #
#
__all__ = ["ListenerPrimitive",
           "PeriodicListener",
           "DelayedListener"]
#
##################


####################
# Constant section #
#
__version__ = "1.6"#current version [major.minor]
#
####################


class ListenerPrimitive(PrimitiveBehavior):
    
    def listen(self, app, graph, node):
        raise NotImplemented

class PeriodicListener(ListenerPrimitive):
    
    def __init__(self, *args, **kwargs):
        self._timeout = kwargs.pop("timeout", 1)
        self._callback = None
        
        assert isinstance(self._timeout, (types.IntType,
                                          types.FloatType))
        
        super(PeriodicListener, self).__init__(*args, **kwargs)
    
    def listen(self, app, thing, node):
        def callback():
            while True:
                yield app.schedule(thing, node, app._start)
                                
                yield app._env.timeout(self._timeout)
        
        app._env.process(callback())

class DelayedListener(ListenerPrimitive):
    
    def __init__(self, *args, **kwargs):
        self._timeout = kwargs.pop("timeout", 1)
        self._callback = None
        
        assert isinstance(self._timeout, (types.IntType,
                                          types.FloatType))
        
        super(DelayedListener, self).__init__(*args, **kwargs)
    
    def listen(self, app, thing, node):
        def callback():
            yield app._env.timeout(self._timeout)
            
            yield app.schedule(thing, node, app._start)
            
        return app._env.process(callback())
            
        