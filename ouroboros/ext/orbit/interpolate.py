#!/usr/bin/env python2.7

"""Interpolator functions

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision
2015-07-25    shenely         1.0         Added new (Hermite) interpolators

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries
from numpy import array
from numpy.polynomial import Polynomial

#Internal libraries
from ouroboros.behavior import behavior,PrimitiveBehavior
from ouroboros.lib.watch import WatcherPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["InterpolatorPrimitive",
           "LinearInterpolator",
           "CubicInterpolator",
           "QuinticInterpolator"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
# 
####################


@behavior(name="InterpolatorPrimitive",
          type="PrimitiveBehavior")
class InterpolatorPrimitive(PrimitiveBehavior,WatcherPrimitive):

    def _process(self,face):
        return self._up(face) \
            if face == "up" else \
            self._eval(face)
    
@behavior(name="LinearInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"t1","type":"DatetimePrimitive"},
                                    {"name":"a1","type":"ArrayPrimitive"},
                                    {"name":"t","type":"DatetimePrimitive"}],
                         "provide":[{"name":"a","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"t1","type":"DatetimePrimitive","args":[]},
                 {"name":"a1","type":"ArrayPrimitive","args":[]},
                 {"name":"t","type":"DatetimePrimitive","args":[]},
                 {"name":"a","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"t1"},
                          "target":{"node":"t1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"a1"},
                          "target":{"node":"a1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"a","face":None},
                          "target":{"node":"SplineInterpolator","face":"a"}}],
                 "control":[]})
class LinearInterpolator(InterpolatorPrimitive):
    
    def _update(self,*args,**kwargs):
        super(LinearInterpolator,self)._update(*args,**kwargs)
        
        self.h00 = Polynomial([1,-1],domain=[0,1])
        self.h01 = Polynomial([0,1],domain=[0,1])

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("t1",)]["obj"].value
        self.a1 = self._data_graph.node[("a1",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = array([0,self.dt])
        self.h00.convert(window=window)
        self.h01.convert(window=window)
        
        logging.info("{0}:  Updated to {1}".\
                     format(self.name,self.t1))
        
        return face
    
    def _eval(self,face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("t",)]["obj"]
        a = self._data_graph.node[("a",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        a.value = self.a0 * self.h00(x) \
                + self.a1 * self.h01(x)
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name,t.value))
    
        return face

@behavior(name="CubicInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"t1","type":"DatetimePrimitive"},
                                    {"name":"v1","type":"ArrayPrimitive"},
                                    {"name":"a1","type":"ArrayPrimitive"},
                                    {"name":"t","type":"DatetimePrimitive"}],
                         "provide":[{"name":"v","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"t1","type":"DatetimePrimitive","args":[]},
                 {"name":"v1","type":"ArrayPrimitive","args":[]},
                 {"name":"a1","type":"ArrayPrimitive","args":[]},
                 {"name":"t","type":"DatetimePrimitive","args":[]},
                 {"name":"v","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"t1"},
                          "target":{"node":"t1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"v1"},
                          "target":{"node":"v1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"a1"},
                          "target":{"node":"a1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"v","face":None},
                          "target":{"node":"SplineInterpolator","face":"v"}}],
                 "control":[]})
class CubicInterpolator(InterpolatorPrimitive):
    
    def _update(self,*args,**kwargs):
        super(CubicInterpolator,self)._update(*args,**kwargs)
        
        self.h00 = Polynomial([1,0,-3,2],domain=[0,1])
        self.h01 = Polynomial([0,0,3,-2],domain=[0,1])
        self.h10 = Polynomial([0,1,-2,1],domain=[0,1])
        self.h11 = Polynomial([0,0,-1,1],domain=[0,1])

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.v0 = self.v1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("t1",)]["obj"].value
        self.v1 = self._data_graph.node[("v1",)]["obj"].value
        self.a1 = self._data_graph.node[("a1",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = array([0,self.dt])
        self.h00.convert(window=window)
        self.h01.convert(window=window)
        self.h10.convert(window=window)
        self.h11.convert(window=window)
        
        logging.info("{0}:  Updated to {1}".\
                     format(self.name,self.t1))
        
        return face
    
    def _eval(self,face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("t",)]["obj"]
        v = self._data_graph.node[("v",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        v.value = self.v0 * self.h00(x) \
                + self.v1 * self.h01(x) \
                + self.a0 * self.h10(x) * self.dt \
                + self.a1 * self.h11(x) * self.dt
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name,t.value))
    
        return face

@behavior(name="QuinticInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"t1","type":"DatetimePrimitive"},
                                    {"name":"p1","type":"ArrayPrimitive"},
                                    {"name":"v1","type":"ArrayPrimitive"},
                                    {"name":"a1","type":"ArrayPrimitive"},
                                    {"name":"t","type":"DatetimePrimitive"}],
                         "provide":[{"name":"p","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"t1","type":"DatetimePrimitive","args":[]},
                 {"name":"p1","type":"ArrayPrimitive","args":[]},
                 {"name":"v1","type":"ArrayPrimitive","args":[]},
                 {"name":"a1","type":"ArrayPrimitive","args":[]},
                 {"name":"t","type":"DatetimePrimitive","args":[]},
                 {"name":"p","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"t1"},
                          "target":{"node":"t1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"p1"},
                          "target":{"node":"p1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"v1"},
                          "target":{"node":"v1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"a1"},
                          "target":{"node":"a1","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"p","face":None},
                          "target":{"node":"SplineInterpolator","face":"p"}}],
                 "control":[]})
class QuinticInterpolator(InterpolatorPrimitive):
    
    def _update(self,*args,**kwargs):
        super(QuinticInterpolator,self)._update(*args,**kwargs)
        
        self.h00 = Polynomial([1,0,0,-10,15,-6],domain=[0,1])
        self.h01 = Polynomial([0,0,0,10,-15,6],domain=[0,1])
        self.h10 = Polynomial([0,1,0,-6,8,-3],domain=[0,1])
        self.h11 = Polynomial([0,0,0,-4,7,-3],domain=[0,1])
        self.h20 = Polynomial([0,0,1,-3,3,-1],domain=[0,1]) / 2
        self.h21 = Polynomial([0,0,0,1,-2,1],domain=[0,1]) / 2

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.p0 = self.p1
        self.v0 = self.v1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("t1",)]["obj"].value
        self.p1 = self._data_graph.node[("p1",)]["obj"].value
        self.v1 = self._data_graph.node[("v1",)]["obj"].value
        self.a1 = self._data_graph.node[("a1",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = array([0,self.dt])
        self.h00.convert(window=window)
        self.h01.convert(window=window)
        self.h10.convert(window=window)
        self.h11.convert(window=window)
        self.h20.convert(window=window)
        self.h21.convert(window=window)
        
        logging.info("{0}:  Updated to {1}".\
                     format(self.name,self.t1))
        
        return face
    
    def _eval(self,face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("t",)]["obj"]
        p = self._data_graph.node[("p",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        p.value = self.p0 * self.h00(x) \
                + self.p1 * self.h01(x) \
                + self.v0 * self.h10(x) * self.dt \
                + self.v1 * self.h11(x) * self.dt \
                + self.a0 * self.h20(x) * self.dt ** 2 \
                + self.a1 * self.h21(x) * self.dt ** 2
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name,t.value))
    
        return face
        
def install(service):
    InterpolatorPrimitive.install(service)
    LinearInterpolator.install(service)
    CubicInterpolator.install(service)
    QuinticInterpolator.install(service)