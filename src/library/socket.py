#!/usr/bin/env python2.7

"""Socket behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 August 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision
2014-08-22    shenely         1.1         Combined behavior and structure

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
from common import ObjectDict
from behavior import *
from . import StringPrimitive,SourcePrimitive,TargetPrimitive
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
__version__ = "1.1"#current version [major.minor]
# 
####################


@required("type",StringPrimitive)
@required("identity",StringPrimitive)
@behavior()
class SocketPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        pins.append(ObjectDict(name="value",value=None))
        
        super(SocketPrimitive,self).__init__(name,pins,*args,**kwargs)
    
    def type(self,value):
        self.value = self._context.socket(getattr(zmq,value.value))
    
    def identity(self,value):
        self.value.setsockopt(zmq.IDENTITY,value.value)
    
@required("socket",SocketPrimitive)
@required("address",StringPrimitive)
@provided("message",StringPrimitive)
@behavior()
class SocketSubscribe(SourcePrimitive):
    
    def socket(self,value):
        assert value.value.socket_type is zmq.SUB
    
    def address(self,value):
        self.socket.value.setsockopt(zmq.SUBSCRIBE,value.value)
    
    def message(self,value):pass
    
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
@behavior()
class SocketPublish(TargetPrimitive):
    
    def socket(self,value):
        assert value.value.socket_type is zmq.PUB
    
    def address(self,value):pass
    
    def message(self,value):pass
           
    def _send(self):
        self.socket.value.send_multipart((self.address.value,
                                          self.message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self._name,self.address.value))