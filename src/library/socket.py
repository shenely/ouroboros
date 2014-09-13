#!/usr/bin/env python2.7

"""Socket behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 September 2014

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
from behavior import *
from . import StringPrimitive,SourcePrimitive,TargetPrimitive
from .event import HandlerEvent
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
__version__ = "1.3"#current version [major.minor]
# 
####################


@required("type",StringPrimitive,
          lambda self,value:\
          setattr(self,"value",self._context.socket(getattr(zmq,value.value))))
@required("identity",StringPrimitive,
          lambda self,value:\
          self.value.setsockopt(zmq.IDENTITY,value.value))
class SocketPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        self._context = zmq.Context(1)
        
        super(SocketPrimitive,self).__init__(name,pins,*args,**kwargs)
    
@required("socket",SocketPrimitive)
@required("address",StringPrimitive,
          lambda self,value:\
          self.socket.value.setsockopt(zmq.SUBSCRIBE,value.value))
@provided("message",StringPrimitive)
class SocketSubscribe(SourcePrimitive,HandlerEvent):
    
    @property
    def handle(self):
        return self.socket
    
    def _receive(self):
        address,message = self.socket.value.recv_multipart()
        
        assert isinstance(address,types.StringTypes)
        assert self.address.value in address
        assert isinstance(message,types.StringTypes)
        
        self.message.value = message
                
        logging.info("{0}:  From address {1}".\
                     format(self._name,self.address.value))

@required("socket",SocketPrimitive)
@required("address",StringPrimitive)
@required("message",StringPrimitive)
class SocketPublish(TargetPrimitive):
           
    def _send(self):
        self.socket.value.send_multipart((self.address.value,
                                          self.message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self._name,self.address.value))