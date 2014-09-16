#!/usr/bin/env python2.7

"""Socket behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 September 2014

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
__version__ = "1.5"#current version [major.minor]
# 
####################

#lambda self,value:\
#self.value.setsockopt(zmq.SUBSCRIBE,"") if getattr(zmq,value.value) == zmq.SUB else None)

@required("type",StringPrimitive,
          lambda self,value:\
          setattr(self,"value",self._context.socket(getattr(zmq,value.value))))
@required("address",StringPrimitive,
          lambda self,value:\
          self.value.connect(value.value))
@required("identity",StringPrimitive,
          lambda self,value:\
          self.value.setsockopt(zmq.IDENTITY,value.value))
class SocketPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        self._context = zmq.Context.instance()
        
        super(SocketPrimitive,self).__init__(name,pins,*args,**kwargs)
    
@required("socket",SocketPrimitive)
@required("address",StringPrimitive)
@provided("message",StringPrimitive)
class SocketSubscribe(SourcePrimitive,HandlerListener):
    
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
                     format(self._name,address))
        
    def listen(self,app):
        self.socket.value.setsockopt(zmq.SUBSCRIBE,self.address.value)
        
        super(SocketSubscribe,self).listen(app)

@required("socket",SocketPrimitive)
@required("address",StringPrimitive)
@required("message",StringPrimitive)
class SocketPublish(TargetPrimitive):
           
    def _send(self):        
        self.socket.value.send_multipart((self.address.value,
                                          self.message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self._name,self.address.value))