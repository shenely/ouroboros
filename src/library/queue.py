#!/usr/bin/env python2.7

"""Queue behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 April 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-11    shenely         1.0         Initial revision
2014-09-15    shenely         1.1         Priority is provided on get
2015-04-21    shenely         1.2         Support for factory rewrite

"""


##################
# Import section #
#
#Built-in libraries
from Queue import PriorityQueue
import logging

#External libraries

#Internal libraries
from behavior import *
from . import EventPrimitive,ActionPrimitive
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
__version__ = "1.2"#current version [major.minor]
# 
####################


@behavior(name="QueuePrimitive",
          type="PrimitiveBehavior")
class QueuePrimitive(PrimitiveBehavior):
    
    def __init__(self,name,*args,**kwargs):
        super(QueuePrimitive,self).__init__(name,*args,**kwargs)
        
        self.value = PriorityQueue()

@behavior(name="QueueGet",
          type="EventPrimitive",
          faces={"data":{"require":[{"name":"queue",
                                     "type":"QueuePrimitive"},
                                    {"name":"priority",
                                     "type":"PrimitiveBehavior"}],
                         "provide":[{"name":"object",
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
class QueueGet(EventPrimitive):
    
    def _occur(self):
        queue = self._data_graph.node["queue"]["obj"]
        priority = self._data_graph.node["priority"]["obj"]
        object = self._data_graph.node["object"]["obj"]
        
        if not queue.value.empty(): 
            priority.value,object.value = queue.value.get()
                    
            logging.info("{0}: Got from queue".\
                         format(self.name))
            
            return Ellipsis,["object"]
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self.name))
            
            return None,[]

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
class QueuePut(ActionPrimitive):
           
    def _execute(self):
        queue = self._data_graph.node["queue"]["obj"]
        priority = self._data_graph.node["priority"]["obj"]
        object = self._data_graph.node["object"]["obj"]
        
        if not queue.value.full():
            queue.value.put((priority.value,
                             object.value))
                    
            logging.info("{0}:  Put to queue".\
                         format(self.name))
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))