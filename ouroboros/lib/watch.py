#!/usr/bin/env python2.7

"""Watching behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   24 July 2015

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
__version__ = "1.3"#current version [major.minor]
#
####################


class WatcherPrimitive(PrimitiveBehavior):
    
    def __init__(self,*args,**kwargs):
        super(WatcherPrimitive,self).__init__(*args,**kwargs)
        
        self._lookback = False
    
    def watch(self,app,root,path,*faces):
        def callback():
            yield app._start
            
            for face in faces:
                node_set = set()
                
                source = root._data_graph.node[path + (face,)].get("obj")
                
                def recursion(e):
                    node_set.add(e)
                    
                    for n in list(node_set):
                        for p in root._data_graph.predecessors_iter(n):
                            if p not in node_set:
                                recursion(p)
                        for s in root._data_graph.successors_iter(n):
                            if s not in node_set:
                                recursion(s)
                
                recursion(path + (face,))
                
                node_set.remove(path + (face,))
                
                for n in node_set:
                    target = root._data_graph.node[n].get("obj")
                    
                    logging.debug("{0}:  Referenced to {1}".\
                                  format(target.name,source.name))
                    
                    if hasattr(source,"value"):
                        if source.value is None and \
                           hasattr(target,"value"):
                            source.value = target.value
                            source.default = target.default
                            source.object_hook = target.object_hook
                        else:
                            target.value = source.value
                            target.default = source.default
                            target.object_hook = source.object_hook
                    elif hasattr(target,"value") and \
                         target.value is not None:
                        source.value = target.value
                        source.default = target.default
                        source.object_hook = target.object_hook
        
        return app._env.process(callback())