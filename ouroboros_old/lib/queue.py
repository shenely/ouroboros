#!/usr/bin/env python2.7

"""Queue behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-11    shenely         1.0         Initial revision
2014-09-15    shenely         1.1         Priority is provided on get
2015-04-21    shenely         1.2         Support for factory rewrite
2015-05-27    shenely         1.3         Graph access by tuple
2015-06-04    shenely         1.4         Moved init to update
2015-07-01    shenely         1.5         Removing unused dependencies
2015-07-24    shenely         1.6         Removed need for thread safety
2016-06-18    shenely         1.7         General code cleanup
"""


##################
# Import section #
#
#Built-in libraries
import heapq
import logging

#External libraries

#Internal libraries
from ..behavior import behavior, PrimitiveBehavior
from . import EventPrimitive, ActionPrimitive
from .watch import WatcherPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["QueuePrimitive",
           "QueueGet",
           "QueuePut"]
#
##################


####################
# Constant section #
#
__version__ = "1.7"#current version [major.minor]
# 
####################


@behavior(name="QueuePrimitive",
          type="PrimitiveBehavior")
class QueuePrimitive(PrimitiveBehavior):
    
    def init(self, *args, **kwargs):
        super(QueuePrimitive, self).init(*args, **kwargs)
        
        self.value = list()

@behavior(name="QueueGet",
          type="EventPrimitive",
          faces={"data":{"require":[{"name":"queue",
                                     "type":"QueuePrimitive"}],
                         "provide":[{"name":"priority",
                                     "type":"PrimitiveBehavior"},
                                    {"name":"object",
                                     "type":"PrimitiveBehavior"}]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"queue",
                  "type":"QueuePrimitive","args":[]},
                 {"name":"priority",
                  "type":"PrimitiveBehavior","args":[]},
                 {"name":"object",
                  "type":"PrimitiveBehavior","args":[]}],
          edges={"data":[{"source":{"node":"QueueGet","face":"queue"},
                          "target":{"node":"queue","face":None}},
                         {"source":{"node":"QueueGet","face":"priority"},
                          "target":{"node":"priority","face":None}},
                         {"source":{"node":"object","face":None},
                          "target":{"node":"QueueGet","face":"object"}}],
                 "control":[]})
class QueueGet(EventPrimitive, WatcherPrimitive):
    
    def _occur(self):
        queue = self._data_graph.node[("queue",)]["obj"]
        priority = self._data_graph.node[("priority",)]["obj"]
        object = self._data_graph.node[("object",)]["obj"]
        
        if len(queue.value) > 0: 
            priority.value, object.value = heapq.heappop(queue.value)
                    
            logging.info("{0}: Got from queue".\
                         format(self.name))
            
            return "output"
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self.name))
            
            return None

@behavior(name="QueuePut",
          type="ActionPrimitive",
          faces={"data":{"require":[{"name":"queue",
                                     "type":"QueuePrimitive"},
                                    {"name":"priority",
                                     "type":"PrimitiveBehavior"},
                                    {"name":"object",
                                     "type":"PrimitiveBehavior"}],
                         "provide":[]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"queue",
                  "type":"QueuePrimitive","args":[]},
                 {"name":"priority",
                  "type":"PrimitiveBehavior","args":[]},
                 {"name":"object",
                  "type":"PrimitiveBehavior","args":[]}],
          edges={"data":[{"source":{"node":"QueuePut","face":"queue"},
                          "target":{"node":"queue","face":None}},
                         {"source":{"node":"QueuePut","face":"priority"},
                          "target":{"node":"priority","face":None}},
                         {"source":{"node":"QueuePut","face":"object"},
                          "target":{"node":"object","face":None}}],
                 "control":[]})
class QueuePut(ActionPrimitive, WatcherPrimitive):
           
    def _execute(self):
        queue = self._data_graph.node[("queue",)]["obj"]
        priority = self._data_graph.node[("priority",)]["obj"]
        object = self._data_graph.node[("object",)]["obj"]
        
        if True:
            heapq.heappush(queue.value,
                           (priority.value, object.value))
                    
            logging.info("{0}:  Put to queue".\
                         format(self.name))
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))