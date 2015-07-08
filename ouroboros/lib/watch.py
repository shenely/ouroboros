#!/usr/bin/env python2.7

"""Watching behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   30 June 2015

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-05-23    shenely         1.0         Initial revision
2015-06-04    shenely         1.1         Its not calling, its watching
2015-06-30    shenely         1.2         Removing unused dependencies

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries

#Internal libraries
from ouroboros.behavior import PrimitiveBehavior
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
__version__ = "1.2"#current version [major.minor]
#
####################


class WatcherPrimitive(PrimitiveBehavior):
    
    def __init__(self,*args,**kwargs):
        super(WatcherPrimitive,self).__init__(*args,**kwargs)
        
        self._lookback = False
    
    def watch(self,app,graph,node):        
        app._process.watch(graph,node,*self._required_data.keys())
        app._process.watch(graph,node,*self._provided_data.keys())
    
#     def __enter__(self):
#         if not self._lookback:
#             self._lookback = True
#             self._loopup(True,*self._required_data.keys())
#          
#         return super(WatcherPrimitive,self).__enter__()
#          
#     def __exit__(self,type,value,traceback):
#         if type is None:
#             self._loopup(False,*self._provided_data.keys())
#             self._lookback = False
#          
#         return super(WatcherPrimitive,self).__exit__(type,value,traceback)