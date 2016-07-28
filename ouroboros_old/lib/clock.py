#!/usr/bin/env python2.7

"""Clock behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

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
2014-09-15    shenely         1.5         Events are now listeners
2014-10-20    shenely         1.6         Propagate clock period to timeout
                                            node
2015-04-21    shenely         1.7         Support for factory rewrite
2015-07-01    shenely         1.8         Added install function
2015-07-07    shenely         1.9         Using JSON parser now
2016-06-18    shenely         1.10        General code cleanup
"""


##################
# Import section #
#
#Built-in libraries
import datetime
import types
import logging

#External libraries
import bson.tz_util

#Internal libraries
from ..behavior import behavior, PrimitiveBehavior
from . import SourcePrimitive
from .watch import WatcherPrimitive
from .listen import PeriodicListener
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
__version__ = "1.10"#current version [major.minor]

UNIX = datetime.datetime(1970, 1, 1, 0,
                         tzinfo=bson.tz_util.utc)
J2000 = datetime.datetime(2000, 1, 1, 12,
                          tzinfo=bson.tz_util.utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_PERIOD = datetime.timedelta(milliseconds=100)
CLOCK_SCALE = 1#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = datetime.timedelta(seconds=60)#Clock step (default to 60 seconds)

# 
####################


@behavior(name="DatetimePrimitive",
          type="PrimitiveBehavior")
class DatetimePrimitive(PrimitiveBehavior):
    
    def init(self, *args, **kwargs):
        self.value = kwargs.pop("value", J2000)
            
        assert isinstance(self.value, datetime.datetime)
        
        super(DatetimePrimitive, self).init(*args, **kwargs)

@behavior(name="ElapsedPrimitive",
          type="PrimitiveBehavior")
class ElapsedPrimitive(PrimitiveBehavior):
    
    def init(self, *args, **kwargs):
        self.value = kwargs.pop("value", CLOCK_STEP)
        
        if isinstance(self.value, types.DictType):
            self.value = self.object_hook(self.value)
        
        assert isinstance(self.value, datetime.timedelta)
        
        super(ElapsedPrimitive, self).init(*args, **kwargs)
        
    def default(self,obj):
        if isinstance(obj, datetime.timedelta):
            obj = {"$elapse": obj.total_seconds()}
        else:
            obj = super(ElapsedPrimitive, self).default(obj)
            
        return obj
        
    def object_hook(self,dct):
        dct = super(ElapsedPrimitive, self).object_hook(dct)
        
        if isinstance(dct, types.DictType):
            if "$elapse" in dct:
                elapsed = dct["$elapse"]
                
                assert isinstance(elapsed, types.IntType)
                
                dct = datetime.timedelta(elapsed)
    
        return dct

@behavior(name="ClockSource",
          type="SourcePrimitive",
          faces={"data":{"require":[{"name":"epoch",
                                     "type":"DatetimePrimitive"},
                                    {"name":"period",
                                     "type":"ElapsedPrimitive"}],
                         "provide":[{"name":"message",
                                     "type":"DatetimePrimitive"}]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"epoch",
                  "type":"DatetimePrimitive","args":[]},
                 {"name":"period",
                  "type":"ElapsedPrimitive","args":[]},
                 {"name":"message",
                  "type":"DatetimePrimitive","args":[]}],
          edges={"data":[{"source":{"node":"ClockSource","face":"epoch"},
                          "target":{"node":"epoch","face":None}},
                         {"source":{"node":"ClockSource","face":"period"},
                          "target":{"node":"period","face":None}},
                         {"source":{"node":"message","face":None},
                          "target":{"node":"ClockSource","face":"message"}}],
                 "control":[]})
class ClockSource(SourcePrimitive, PeriodicListener, WatcherPrimitive):
    
    def init(self, *args, **kwargs):
        kwargs["epoch"] = kwargs.get("epoch", J2000)
        kwargs["period"] = kwargs.get("period", CLOCK_PERIOD)
            
        super(ClockSource, self).init(*args, **kwargs)
    
    def _receive(self):
        message = self._data_graph.node[("message",)]["obj"]
        
        logging.info("{0}:  Ticking from {1}".\
                     format(self.name, message.value))
        
        self._tick()
                
        logging.info("{0}:  Ticked to {1}".\
                     format(self.name, message.value))
    
    def _tick(self):
        raise NotImplemented

@behavior(name="ContinuousClock",
          type="ClockSource",
          faces={"data":{"require":[{"name":"epoch",
                                     "type":"DatetimePrimitive"},
                                    {"name":"period",
                                     "type":"ElapsedPrimitive"},
                                    {"name":"scale",
                                     "type":"NumberPrimitive"}],
                         "provide":[{"name":"message",
                                     "type":"DatetimePrimitive"}]},
                 "control":{"input":["input"],
                            "output":["output"]}},
          nodes=[{"name":"epoch",
                  "type":"DatetimePrimitive","args":[]},
                 {"name":"period",
                  "type":"ElapsedPrimitive","args":[]},
                 {"name":"scale",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"message",
                  "type":"DatetimePrimitive","args":[]}],
          edges={"data":[{"source":{"node":"ContinuousClock","face":"epoch"},
                          "target":{"node":"epoch","face":None}},
                         {"source":{"node":"ContinuousClock","face":"period"},
                          "target":{"node":"period","face":None}},
                         {"source":{"node":"ContinuousClock","face":"scale"},
                          "target":{"node":"scale","face":None}},
                         {"source":{"node":"message","face":None},
                          "target":{"node":"ContinuousClock","face":"message"}}],
                 "control":[]})
class ContinuousClock(ClockSource):
    
    def __init__(self, name, *args, **kwargs):
        super(ContinuousClock, self).__init__(name, *args, **kwargs)
        
        self._then = datetime.datetime.utcnow()
        
    def init(self, *args, **kwargs):
        kwargs["scale"] = kwargs.get("scale", CLOCK_SCALE)
        
        super(ContinuousClock, self).init(*args, **kwargs)
    
    def _tick(self):
        message = self._data_graph.node[("message",)]["obj"]
        scale = self._data_graph.node[("scale",)]["obj"]
            
        self._now = datetime.datetime.utcnow()
        
        #Increase simulation time
        message.value = message.value +\
                        int(scale.value) * (self._now - self._then)
                             
        self._then = self._now
        
@behavior(name="DiscreteClock",
          type="ClockSource",
          faces={"data":{"require":[{"name":"epoch",
                                     "type":"DatetimePrimitive"},
                                    {"name":"period",
                                     "type":"ElapsedPrimitive"},
                                    {"name":"step",
                                     "type":"ElapsedPrimitive"}],
                         "provide":[{"name":"message",
                                     "type":"DatetimePrimitive"}]},
                 "control":{"input":[],
                            "output":["output"]}},
          nodes=[{"name":"epoch",
                  "type":"DatetimePrimitive","args":[]},
                 {"name":"period",
                  "type":"ElapsedPrimitive","args":[]},
                 {"name":"step",
                  "type":"ElapsedPrimitive","args":[]},
                 {"name":"message",
                  "type":"DatetimePrimitive","args":[]}],
          edges={"data":[{"source":{"node":"DiscreteClock","face":"epoch"},
                          "target":{"node":"epoch","face":None}},
                         {"source":{"node":"DiscreteClock","face":"period"},
                          "target":{"node":"period","face":None}},
                         {"source":{"node":"DiscreteClock","face":"step"},
                          "target":{"node":"step","face":None}},
                         {"source":{"node":"message","face":None},
                          "target":{"node":"DiscreteClock","face":"message"}}],
                 "control":[]})
class DiscreteClock(ClockSource):
    
    def __init__(self, name, *args, **kwargs):
        kwargs["step"] = kwargs.get("step", CLOCK_STEP)
            
        super(DiscreteClock, self).__init__(name, *args, **kwargs)
    
    def _tick(self, message):
        message = self._data_graph.node["message"]["obj"]
        step = self._data_graph.node["step"]["obj"]
        
        #Increase simulation time
        message.value = message.value + step.value