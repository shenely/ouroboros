#!/usr/bin/env python2.7

"""Clock behaviors

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
from datetime import datetime,timedelta
import types
import logging

#External libraries
from bson import json_util
from bson.tz_util import utc

#Internal libraries
from structure import *
from common import ObjectDict
from behavior import PrimitiveBehavior
from . import NumberPrimitive,SourcePrimitive
#
##################=


##################
# Export section #
#
__all__ = ["DatetimePrimitive",
           "ElapsedPrimitive",
           "ContinuousClock",
           "DiscreteClock"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 1.0#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)
# 
####################


@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class DatetimePrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "value":
                assert isinstance(pin.value,datetime)
                
                break
        else:
            pins.append(ObjectDict(name="value",
                                   value=J2000))
        
        super(DatetimePrimitive,self).__init__(name,pins,*args,**kwargs)

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class ElapsedPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "value":
                try:
                    assert isinstance(pin.value,timedelta)
                except AssertionError:
                    assert isinstance(pin.value,types.IntType)
                    
                    pin.value = timedelta(seconds=pin.value)
                
                break
        else:
            pins.append(ObjectDict(name="value",
                                   value=CLOCK_STEP))
        
        super(ElapsedPrimitive,self).__init__(name,pins,*args,**kwargs)
        
    @staticmethod
    def default(obj):
        if isinstance(obj,timedelta):
            obj = { "$elapse": obj.total_seconds() }
        else:
            obj = json_util.default(obj)
            
        return obj
        
    @staticmethod
    def object_hook(dct):
        dct = json_util.object_hook(dct)
        
        if isinstance(dct,types.DictType):
            if "$elapse" in dct:
                elapsed = dct["$elapse"]
                
                assert isinstance(elapsed,types.IntType)
                
                dct = timedelta(elapsed)
    
        return dct
  
@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")      
class ClockSource(SourcePrimitive):
    
    @required(DatetimePrimitive)
    def epoch(self,value):
        self.message.value = value.value
    
    @provided(DatetimePrimitive)
    def message(self,value):pass
    
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self._name,self.message.value))
        
        self._tick()
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self._name,self.message.value))

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class ContinuousClock(ClockSource):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "scale":break
        else:
            pin.append(ObjectDict(name="scale",
                                  value=CLOCK_SCALE))
            
        super(ContinuousClock,self).__init__(*args,**kwargs)
        
        self._then = datetime.utcnow()
    
    @required(NumberPrimitive)
    def scale(self,value):pass
    
    def _tick(self):        
        self._now = datetime.utcnow()
            
        #Increase simulation time
        self.message.value = self.message.value +\
                             self.scale.value * (self._now - self._then)
        
@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class DiscreteClock(ClockSource):
    
    @required(ElapsedPrimitive)
    def step(self,value):pass
    
    def _tick(self):
        #Increase simulation time
        self.message.value = self.message.value +\
                             self.step.value