#!/usr/bin/env python2.7

"""Clock behaviors

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
2014-09-10    shenely         1.2         Clocks work now
2014-09-11    shenely         1.3         Organized behavior decorators
2014-09-12    shenely         1.4         Added event mixins
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta
import types
import logging

#External libraries
from bson.tz_util import utc

#Internal libraries
from common import ObjectDict
from behavior import *
from . import NumberPrimitive,SourcePrimitive
from .event import PeriodicEvent
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
__version__ = "1.4"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_PERIOD = timedelta(milliseconds=100)
CLOCK_SCALE = 1#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)

# 
####################


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

class ElapsedPrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "value":
                assert isinstance(pin.value,timedelta)
                
                break
        else:
            pins.append(ObjectDict(name="value",
                                   value=CLOCK_STEP))
        
        super(ElapsedPrimitive,self).__init__(name,pins,*args,**kwargs)
        
    def default(self,obj):
        if isinstance(obj,timedelta):
            obj = { "$elapse": obj.total_seconds() }
        else:
            obj = super(ElapsedPrimitive,self).default(obj)
            
        return obj
        
    def object_hook(self,dct):
        dct = super(ElapsedPrimitive,self).object_hook(dct)
        
        if isinstance(dct,types.DictType):
            if "$elapse" in dct:
                elapsed = dct["$elapse"]
                
                assert isinstance(elapsed,types.IntType)
                
                dct = timedelta(elapsed)
    
        return dct
  
@required("epoch",DatetimePrimitive,
          lambda self,value:\
          setattr(self.message,"value",value.value))
@provided("message",DatetimePrimitive)
@required("period",ElapsedPrimitive)
class ClockSource(SourcePrimitive,PeriodicEvent):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "period":break
        else:
            pins.append(ObjectDict(name="period",
                                   value=CLOCK_PERIOD))
            
        super(ClockSource,self).__init__(name,pins,*args,**kwargs)
        
        self._then = datetime.utcnow()
    
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self._name,self.message.value))
        
        self._tick()
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self._name,self.message.value))

@required("scale",NumberPrimitive)
class ContinuousClock(ClockSource):
    
    def __init__(self,name,pins,*args,**kwargs):
        for pin in pins:
            if pin.name == "scale":break
        else:
            pins.append(ObjectDict(name="scale",
                                   value=CLOCK_SCALE))
            
        super(ContinuousClock,self).__init__(name,pins,*args,**kwargs)
        
        self._then = datetime.utcnow()
    
    def _tick(self):        
        self._now = datetime.utcnow()
            
        #Increase simulation time
        self.message.value = self.message.value +\
                             int(self.scale.value) * (self._now - self._then)
                             
        self._then = self._now
        
@required("step",ElapsedPrimitive)
class DiscreteClock(ClockSource):
    
    def _tick(self):
        #Increase simulation time
        self.message.value = self.message.value +\
                             self.step.value