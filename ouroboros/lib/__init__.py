#!/usr/bin/env python2.7

"""Behavior library

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   01 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision
2014-08-22    shenely         1.1         Combined behavior and structure
2014-09-10    shenely         1.2         Forcing everything to strings
2014-09-11    shenely         1.3         Organized behavior decorators
2014-10-15    shenely         1.4         Removed messaging arguments
2015-06-04    shenely         1.5         Added checks to primitives
2015-07-01    shenely         1.6         Added install function

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries

#Internal libraries
from ouroboros.common import ObjectDict
from ouroboros.behavior import *
#
##################=


##################
# Export section #
#
__all__ = ["NumberPrimitive",
           "StringPrimitive",
           "SourcePrimitive",
           "TargetPrimitive",
           "ConditionPrimitive",
           "EventPrimitive",
           "ActionPrimitive"]
#
##################


####################
# Constant section #
#
__version__ = "1.7"#current version [major.minor]
# 
####################


@behavior(name="NumberPrimitive",
          type="PrimitiveBehavior")
class NumberPrimitive(PrimitiveBehavior):
    
    def _update(self,*args,**kwargs):
        self.value = kwargs.pop("value",None)
        
        assert isinstance(self.value,(types.IntType,
                                      types.FloatType,
                                      types.ComplexType)) or \
               self.value is None
        
        super(NumberPrimitive,self)._update(*args,**kwargs)

@behavior(name="StringPrimitive",
          type="PrimitiveBehavior")
class StringPrimitive(PrimitiveBehavior):
    
    def _update(self,*args,**kwargs):
        self._value = None
        self.value = kwargs.pop("value",None)

        assert isinstance(self.value,types.StringTypes) or \
               self.value is None
        
        super(StringPrimitive,self)._update(*args,**kwargs)
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self,value):
        self._value = str(value) \
                      if isinstance(value,types.UnicodeType) \
                      else value

@behavior(name="SourcePrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list(),
                                  output=list("output"))))
class SourcePrimitive(PrimitiveBehavior):
    
    def _process(self,face):
        logging.debug("{0}:  Receiving".\
                      format(self.name))
        
        self._receive()
        
        logging.debug("{0}:  Received".\
                      format(self.name))
        
        return "output"
    
    def _receive(self):
        raise NotImplemented
    
@behavior(name="TargetPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list())))
class TargetPrimitive(PrimitiveBehavior):
    
    def _process(self,face):
        logging.debug("{0}:  Sending".\
                      format(self.name))
        
        self._send()
        
        logging.debug("{0}:  Sent".\
                      format(self.name))
        
        return None
    
    def _send(self):
        raise NotImplemented


@behavior(name="ConditionPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=[True,False])))
class ConditionPrimitive(PrimitiveBehavior):
    
    def _process(self,face):
        logging.debug("{0}:  Satisfying".\
                      format(self.name))
        
        state = self._satisfy()
            
        if state is True:
            logging.debug("{0}:  Satisfied".\
                          format(self.name))
        else:
            logging.warning("{0}:  Not satisfied".\
                         format(self.name))
            
        return state
    
    def _satisfy(self):
        raise NotImplemented

@behavior(name="EventPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list("output"))))
class EventPrimitive(PrimitiveBehavior):
    
    def _process(self,face):
        logging.debug("{0}:  Occurring".\
                      format(self.name))
        
        state = self._occur()
        
        if state is not None:
            logging.debug("{0}:  Occurred".\
                         format(self.name))
        else:
            logging.warn("{0}:  False alarm".\
                         format(self.name))
            
        return state
    
    def _occur(self):
        raise NotImplemented

@behavior(name="ActionPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list("output"))))
class ActionPrimitive(PrimitiveBehavior):
    
    def _process(self,face):
        logging.debug("{0}:  Executing".\
                      format(self.name))
        
        faces = self._execute()
        
        logging.debug("{0}:  Executed".\
                     format(self.name))
            
        return "output"
    
    def _execute(self):
        raise NotImplemented
    
def install(service):
    NumberPrimitive.install(service)
    StringPrimitive.install(service)
    SourcePrimitive.install(service)
    TargetPrimitive.install(service)
    ConditionPrimitive.install(service)
    EventPrimitive.install(service)
    ActionPrimitive.install(service)
    
    from . import clock as _
    _.install(service)
    
    from . import message as _
    _.install(service)
    
    from . import order as _
    _.install(service)
    
    from . import queue as _
    _.install(service)
    
    from . import socket as _
    _.install(service)
        