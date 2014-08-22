#!/usr/bin/env python2.7

"""Behavior library

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
__version__ = "1.1"#current version [major.minor]
# 
####################

@behavior()
class NumberPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "value":
                assert isinstance(pin.value,(types.IntType,
                                             types.FloatType,
                                             types.ComplexType))
            
                break
        else:
            pins.append(ObjectDict(name="value",value=0.0))
        
        super(NumberPrimitive,self).__init__(name,pins,*args,**kwargs)

@behavior()
class StringPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "value":
                assert isinstance(pin.value,types.StringTypes)
            
                break
        else:
            pins.append(ObjectDict(name="value",value=""))
        
        super(StringPrimitive,self).__init__(name,pins,*args,**kwargs)

@provided("message",PrimitiveBehavior)
@behavior()
class SourcePrimitive(PrimitiveBehavior):
    
    def message(self):pass
    
    def _process(self):
        logging.debug("{0}:  Receiving".\
                      format(self._name))
        
        self._receive()
        
        logging.debug("{0}:  Received".\
                      format(self._name))
        
        return Ellipsis
    
    def _receive(self):
        raise NotImplemented
    
@provided("message",PrimitiveBehavior)
@behavior()
class TargetPrimitive(PrimitiveBehavior):
    
    def message(self):pass
    
    def _process(self):
        logging.debug("{0}:  Sending".\
                      format(self._name))
        
        self._send()
        
        logging.debug("{0}:  Sent".\
                      format(self._name))
        
        return Ellipsis
    
    def _send(self,message):
        raise NotImplemented

@behavior()
class ConditionPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Satisfying".\
                      format(self._name))
            
        if self._satisfy():
            logging.debug("{0}:  Satisfied".\
                          format(self._name))
            
            return True
        else:
            logging.warning("{0}:  Not satisfied".\
                         format(self._name))
            
            return False
    
    def _satisfy(self,message):
        raise NotImplemented

@behavior()
class EventPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Occurring".\
                      format(self._name))
        
        if self._occur() is not None:
            logging.debug("{0}:  Occurred".\
                         format(self._name))
            
            return Ellipsis
        else:
            logging.warn("{0}:  False alarm".\
                         format(self._name))
            
            return None
    
    def _occur(self):
        raise NotImplemented

@behavior()
class ActionPrimitive(PrimitiveBehavior):
    
    def _process(self):
        logging.debug("{0}:  Executing".\
                      format(self._name))
        
        self._execute()
        
        logging.debug("{0}:  Executed".\
                     format(self._name))
            
        return Ellipsis
    
    def _execute(self):
        raise NotImplemented
        