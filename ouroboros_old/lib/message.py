#!/usr/bin/env python2.7

"""Message behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision
2014-08-22    shenely         1.1         Combined behavior and structure
2014-09-10    shenely         1.2         Using JSON the right way
2014-09-11    shenely         1.3         Organized behavior decorators
2014-09-15    shenely         1.4         Parsing returns something
2014-10-15    shenely         1.5         Modify behaviors, not values
2015-04-21    shenely         1.6         Support for factory rewrite
2015-07-01    shenely         1.7         Removing unused dependencies
2016-06-18    shenely         1.8         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import logging
import json

#External libraries

#Internal libraries
from ..behavior import behavior
from . import EventPrimitive, ActionPrimitive
from .watch import WatcherPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["MessageParse",
           "MessageFormat"]
#
##################


####################
# Constant section #
#
__version__ = "1.8"#current version [major.minor]
# 
####################


@behavior(name="MessageParse",
          type="EventPrimitive",
          faces={"data":{"require":[{"name":"message",
                                     "type":"StringPrimitive"}],
                         "provide":[{"name":"object",
                                     "type":"PrimitiveBehavior"}]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"message",
                  "type":"StringPrimitive","args":[]},
                 {"name":"object",
                  "type":"PrimitiveBehavior","args":[]}],
          edges={"data":[{"source":{"node":"MessageParse","face":"message"},
                          "target":{"node":"message","face":None}},
                         {"source":{"node":"object","face":None},
                          "target":{"node":"MessageParse","face":"object"}}],
                 "control":[]})
class MessageParse(EventPrimitive, WatcherPrimitive):
    
    def _occur(self):
        message = self._data_graph.node[("message",)]["obj"]
        object = self._data_graph.node[("object",)]["obj"]
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name, message.value))
        
        object.value = json.loads(message.value,
                                  object_hook=object.object_hook)
        
        logging.info("{0}:  Parsed to {1!s}".\
                     format(self.name, object.value))
        
        return "output"

@behavior(name="MessageFormat",
          type="ActionPrimitive",
          faces={"data":{"require":[{"name":"object",
                                     "type":"PrimitiveBehavior"}],
                         "provide":[{"name":"message",
                                     "type":"StringPrimitive"}]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"object",
                  "type":"PrimitiveBehavior","args":[]},
                 {"name":"message",
                  "type":"StringPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"MessageFormat","face":"object"},
                          "target":{"node":"object","face":None}},
                         {"source":{"node":"message","face":None},
                          "target":{"node":"MessageFormat","face":"message"}}],
                 "control":[]})
class MessageFormat(ActionPrimitive, WatcherPrimitive):
    
    def _execute(self):
        object = self._data_graph.node[("object",)]["obj"]
        message = self._data_graph.node[("message",)]["obj"]
        
        logging.info("{0}:  Formatting from {1!s}".\
                     format(self.name, object.value))
        
        message.value = json.dumps(object.value,
                                   default=object.default)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name, message.value))
        
        return "output"