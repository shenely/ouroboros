#!/usr/bin/env python2.7

"""Watching behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   23 May 2015

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-05-23    shenely         1.0         Initial revision

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
__all__ = ["WatcherPrimitive"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class WatcherPrimitive(PrimitiveBehavior):
    
    def __init__(self,*args,**kwargs):
        super(WatcherPrimitive,self).__init__(*args,**kwargs)
        
        self._lookback = False
        self._lookahead = False
    
    def watch(self,app,graph,node):
            
        def caller(force,*faces):
            for face in faces:
                app._process.reference(graph,node + (face,))
                
            if app._process._running and force and len(faces) > 0:
                app._process.interrupt()
                
        self._loopup = caller
        
        self._loopup(False,*self._required_data.keys())
        self._loopup(False,*self._provided_data.keys())
    
    def __enter__(self):
        if not self._lookback:
            self._lookback = True
            self._loopup(True,*self._required_data.keys())
        else:
            self._lookback = False
        
        return super(WatcherPrimitive,self).__enter__()
        
    def __exit__(self,type,value,traceback):
        if type is None:
            if not self._lookahead:
                self._lookahead = True
                self._loopup(False,*self._provided_data.keys())
            else:
                self._lookahead = False
        
        return super(WatcherPrimitive,self).__exit__(type,value,traceback)