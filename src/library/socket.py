#!/usr/bin/env python2.7

"""Socket behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 April 2014

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
from behavior import behavior,PrimitiveBehavior
from . import StringPrimitive,SourcePrimitive,TargetPrimitive
from .listen import HandlerListener
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
__version__ = "1.6"#current version [major.minor]
# 
####################


@behavior(name="QueuePrimitive",
          type="PrimitiveBehavior",
          faces={"data":{"require":[],
                         "provide":[]},
                 "control":{"input":[],
                            "output":["output"]}},
          nodes=[{"name":"type",
                  "type":"StringPrimitive","args":[]},
                 {"name":"address",
                  "type":"StringPrimitive","args":[]},
                 {"name":"identity",
                  "type":"StringPrimitive","args":[]}])
class SocketPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        super(SocketPrimitive,self).__init__(name,pins,*args,**kwargs)
        
        type = kwargs.get("type")
        address = kwargs.get("address")
        identity = kwargs.get("identity")
        
        context = zmq.Context.instance()
        
        self.value = context.socket(getattr(zmq,type))
        self.value.connect(address)
        self.value.setsockopt(zmq.IDENTITY,identity)

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
class SocketSubscribe(SourcePrimitive,HandlerListener):
    
    @property
    def handle(self):
        return self._data_graph.node["socket"].value
    
    def _receive(self):
        socket = self._data_graph.node["socket"]
        address = self._data_graph.node["address"]
        message = self._data_graph.node["message"]
        
        temp = socket.value.recv_multipart()
        
        assert isinstance(temp,types.TupleType) and len(type) == 2
        assert isinstance(temp[0],types.StringTypes)
        assert address.value in temp[0]
        assert isinstance(temp[1],types.StringTypes)
        
        message.value = message
                
        logging.info("{0}:  From address {1}".\
                     format(self.name,address.value))
        
        return ["message"]
        
    def listen(self,app,graph,node):
        socket = self._data_graph.node["socket"]
        address = self._data_graph.node["address"]
        
        socket.value.setsockopt(zmq.SUBSCRIBE,address.value)
        
        super(SocketSubscribe,self).listen(app,graph,node)

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
class SocketPublish(TargetPrimitive):
           
    def _send(self):
        socket = self._data_graph.node["socket"]
        address = self._data_graph.node["address"]
        message = self._data_graph.node["message"]
        
        socket.value.send_multipart((address.value,
                                     message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self.name,address.value))