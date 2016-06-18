#!/usr/bin/env python2.7

"""Socket behaviors

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
2014-09-10    shenely         1.2         Got sockets to work
2014-09-11    shenely         1.3         Organized behavior decorators
2014-09-12    shenely         1.4         Added event mixins
2014-09-15    shenely         1.5         Got two sockets communicating
2015-04-21    shenely         1.6         Support for factory rewrite
2015-06-04    shenely         1.7         Graph access by tuple
2015-07-01    shenely         1.8         Added install function
2015-07-02    shenely         1.9         Cleaned up behavior definitions
2016-06-18    shenely         1.10         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries
import zmq

#Internal libraries
from ..behavior import behavior, PrimitiveBehavior
from . import SourcePrimitive,TargetPrimitive
from .listen import HandlerListener
from .watch import WatcherPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["SocketPrimitive",
           "SocketSubscribe",
           "SocketPublish"]
#
##################


####################
# Constant section #
#
__version__ = "1.10"#current version [major.minor]
# 
####################


@behavior(name="SocketPrimitive",
          type="PrimitiveBehavior",
          nodes=[{"name":"type",
                  "type":"StringPrimitive","args":[]},
                 {"name":"address",
                  "type":"StringPrimitive","args":[]}])
class SocketPrimitive(PrimitiveBehavior):
    
    def init(self, *args, **kwargs):
        super(SocketPrimitive, self).init(*args, **kwargs)
        
        type = kwargs.get("type")
        address = kwargs.get("address")
        
        if type is not None and \
           address is not None:
            context = zmq.Context.instance()
            
            self.value = context.socket(getattr(zmq,type))
            self.value.connect(address)
        else:
            self.value = None

@behavior(name="SocketSubscribe",
          type="SourcePrimitive",
          faces={"data":{"require":[{"name":"socket",
                                     "type":"SocketPrimitive"},
                                    {"name":"address",
                                     "type":"StringPrimitive"}],
                         "provide":[{"name":"message",
                                     "type":"StringPrimitive"}]},
                 "control":{"input":[],
                            "output":["output"]}},
          nodes=[{"name":"socket",
                  "type":"SocketPrimitive","args":[]},
                 {"name":"address",
                  "type":"StringPrimitive","args":[]},
                 {"name":"message",
                  "type":"StringPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SocketSubscribe","face":"socket"},
                          "target":{"node":"socket","face":None}},
                         {"source":{"node":"SocketSubscribe","face":"address"},
                          "target":{"node":"address","face":None}},
                         {"source":{"node":"message","face":None},
                          "target":{"node":"SocketSubscribe","face":"message"}}],
                 "control":[]})
class SocketSubscribe(SourcePrimitive, HandlerListener, WatcherPrimitive):
    
    @property
    def handle(self):
        return self._data_graph.node[("socket",)]["obj"].value
    
    def _receive(self):
        socket = self._data_graph.node[("socket",)]["obj"]
        address = self._data_graph.node[("address",)]["obj"]
        message = self._data_graph.node[("message",)]["obj"]
        
        temp = socket.value.recv_multipart()
        
        assert isinstance(temp, types.ListType) and len(temp) == 2
        assert isinstance(temp[0], types.StringTypes)
        assert address.value in temp[0]
        assert isinstance(temp[1], types.StringTypes)
        
        message.value = temp[1]
                
        logging.info("{0}:  From address {1}".\
                     format(self.name, address.value))
        
    def listen(self,app, graph,node):
        socket = self._data_graph.node[("socket",)]["obj"]
        address = self._data_graph.node[("address",)]["obj"]
        
        def caller():
            socket.value.setsockopt(zmq.SUBSCRIBE, address.value)
            
        self._caller = caller
                    
        super(SocketSubscribe, self).listen(app, graph, node)

@behavior(name="SocketPublish",
          type="TargetPrimitive",
          faces={"data":{"require":[{"name":"socket",
                                     "type":"SocketPrimitive"},
                                    {"name":"address",
                                     "type":"StringPrimitive"},
                                    {"name":"message",
                                     "type":"StringPrimitive"}],
                         "provide":[]},
                 "control":{"input":["input"],
                            "output":[]}},
          nodes=[{"name":"socket",
                  "type":"SocketPrimitive","args":[]},
                 {"name":"address",
                  "type":"StringPrimitive","args":[]},
                 {"name":"message",
                  "type":"StringPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SocketPublish","face":"socket"},
                          "target":{"node":"socket","face":None}},
                         {"source":{"node":"SocketPublish","face":"address"},
                          "target":{"node":"address","face":None}},
                         {"source":{"node":"SocketPublish","face":"message"},
                          "target":{"node":"message","face":None}}],
                 "control":[]})
class SocketPublish(TargetPrimitive, WatcherPrimitive):
           
    def _send(self):
        socket = self._data_graph.node[("socket",)]["obj"]
        address = self._data_graph.node[("address",)]["obj"]
        message = self._data_graph.node[("message",)]["obj"]
        
        socket.value.send_multipart((address.value,
                                     message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self.name, address.value))
    
def install(service):
    SocketPrimitive.install(service)
    SocketSubscribe.install(service)
    SocketPublish.install(service)