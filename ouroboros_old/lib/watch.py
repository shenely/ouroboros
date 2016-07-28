#!/usr/bin/env python2.7

"""Watching behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-05-23    shenely         1.0         Initial revision
2015-06-04    shenely         1.1         Its not calling, its watching
2015-06-30    shenely         1.2         Removing unused dependencies
2015-07-24    shenely         1.3         Looks more like listeners now
2016-06-18    shenely         1.4         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries

#Internal libraries
from ..behavior import PrimitiveBehavior
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
__version__ = "1.4"#current version [major.minor]
#
####################


class WatcherPrimitive(PrimitiveBehavior):
    
    def __init__(self, *args, **kwargs):
        super(WatcherPrimitive, self).__init__(*args, **kwargs)
        
        self._lookback = False
    
    def watch(self, app, root, path, *faces):
        for face in faces:
            nodes = set()
            
            source = root._data_graph.node[path + (face,)].get("obj")
            
            def recursion(e):
                nodes.add(e)
                
                for n in list(nodes):
                    for p in root._data_graph.predecessors_iter(n):
                        if p not in nodes:
                            recursion(p)
                    for s in root._data_graph.successors_iter(n):
                        if s not in nodes:
                            recursion(s)
            
            recursion(path + (face,))
            
            nodes.remove(path + (face,))
            
            for n in nodes:
                target = root._data_graph.node[n].get("obj")
                
                logging.debug("{0}:  Referenced to {1}".\
                              format(target.name, source.name))
                
                if hasattr(source, "value"):
                    if source.value is None and \
                       hasattr(target, "value"):
                        source.value = target.value
                        source.default = target.default
                        source.object_hook = target.object_hook
                    else:
                        target.value = source.value
                        target.default = source.default
                        target.object_hook = source.object_hook
                elif hasattr(target, "value") and \
                     target.value is not None:
                    source.value = target.value
                    source.default = target.default
                    source.object_hook = target.object_hook