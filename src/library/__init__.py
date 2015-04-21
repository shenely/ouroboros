#!/usr/bin/env python2.7

"""Behavior library

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 April 2015

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
2015-04-21    shenely         1.5         Support for factory rewrite

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

#External libraries

#Internal libraries
from common import ObjectDict
from behavior import *
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
__version__ = "1.5"#current version [major.minor]
# 
####################


@behavior(name="NumberPrimitive",
          type="PrimitiveBehavior")
class NumberPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,*args,**kwargs):
        self.value = kwargs.pop("value",0.0)
        
        assert isinstance(self.value,(types.IntType,
                                      types.FloatType,
                                      types.ComplexType))
        
        super(NumberPrimitive,self).__init__(name,*args,**kwargs)

@behavior(name="StringPrimitive",
          type="PrimitiveBehavior")
class StringPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,*args,**kwargs):
        self.value = kwargs.pop("value","")
        
        assert isinstance(self.value,types.StringTypes)
        
        super(StringPrimitive,self).__init__(name,*args,**kwargs)

@behavior(name="SourcePrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list(),
                                  output=list("output"))))
class SourcePrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Receiving".\
                      format(self.name))
        
        faces = self._receive()
        
        logging.debug("{0}:  Received".\
                      format(self.name))
        
        return "output",faces
    
    def _receive(self):
        raise NotImplemented
    
@behavior(name="TargetPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list())))
class TargetPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Sending".\
                      format(self.name))
        
        faces = self._receive()
        
        logging.debug("{0}:  Sent".\
                      format(self.name))
        
        return None,faces
    
    def _send(self):
        raise NotImplemented


@behavior(name="ConditionPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=[True,False])))
class ConditionPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Satisfying".\
                      format(self.name))
        
        state,faces = self._satisfy()
            
        if state is True:
            logging.debug("{0}:  Satisfied".\
                          format(self.name))
        else:
            logging.warning("{0}:  Not satisfied".\
                         format(self.name))
            
        return state,faces
    
    def _satisfy(self):
        raise NotImplemented

@behavior(name="EventPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list("output"))))
class EventPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Occurring".\
                      format(self.name))
        
        state,faces = self._occur()
        
        if state is not None:
            logging.debug("{0}:  Occurred".\
                         format(self.name))
        else:
            logging.warn("{0}:  False alarm".\
                         format(self.name))
            
        return state,faces
    
    def _occur(self):
        raise NotImplemented

@behavior(name="ActionPrimitive",
          type="PrimitiveBehavior",
          faces=dict(data=dict(require=list(),
                               provide=list()),
                     control=dict(input=list("input"),
                                  output=list("output"))))
class ActionPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Executing".\
                      format(self.name))
        
        faces = self._execute()
        
        logging.debug("{0}:  Executed".\
                     format(self.name))
            
        return "output",faces
    
    def _execute(self):
        raise NotImplemented
        