#!/usr/bin/env python2.7

"""Socket behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 August 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision

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
from structure import *
from common import ObjectDict
from behavior import PrimitiveBehavior
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
__version__ = "1.0"#current version [major.minor]
# 
####################


@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class SocketPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        pins.append(ObjectDict(name="value",value=None))
        
        super(SocketPrimitive,self).__init__(name,pins,*args,**kwargs)
    
    @required(StringPrimitive)
    def type(self,value):
        self.value = self._context.socket(getattr(zmq,value.value))
    
    @required(StringPrimitive)
    def identity(self,value):
        self.value.setsockopt(zmq.IDENTITY,value.value)
    
@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class SocketSubscribe(SourcePrimitive):
    
    @required(SocketPrimitive)
    def socket(self,value):
        assert value.value.socket_type is zmq.SUB
    
    @required(StringPrimitive)
    def address(self,value):
        self.socket.value.setsockopt(zmq.SUBSCRIBE,value.value)
    
    @provided(StringPrimitive)
    def message(self,value):pass
    
    def _receive(self):
        address,message = self.socket.value.recv_multipart()
        
        assert isinstance(address,types.StringTypes)
        assert self.address.value in address
        assert isinstance(message,types.StringTypes)
        
        self.message.value = message
                
        logging.info("{0}:  From address {1}".\
                     format(self._name,self.address.value))

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class SocketPublish(TargetPrimitive):
    
    @required(SocketPrimitive)
    def socket(self,value):
        assert value.value.socket_type is zmq.PUB
    
    @required(StringPrimitive)
    def address(self,value):pass
    
    @required(StringPrimitive)
    def message(self,value):pass
           
    def _send(self):
        self.socket.value.send_multipart((self.address.value,
                                          self.message.value))
                
        logging.info("{0}:  To address {1}".\
                     format(self._name,self.address.value))