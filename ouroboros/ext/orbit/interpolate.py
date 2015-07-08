#!/usr/bin/env python2.7

"""Interpolator functions

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   07 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision

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
           "KinematicInterpolator",
           "SplineInterpolator"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################


@behavior(name="InterpolatorPrimitive",
          type="PrimitiveBehavior")
class InterpolatorPrimitive(PrimitiveBehavior,WatcherPrimitive):

    def _process(self,face):
        return self._up(face) \
            if face == "up" else \
            self._eval(face)

@behavior(name="KinematicInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"up_t","type":"DatetimePrimitive"},
                                    {"name":"up_p","type":"ArrayPrimitive"},
                                    {"name":"up_v","type":"ArrayPrimitive"},
                                    {"name":"t","type":"DatetimePrimitive"}],
                         "provide":[{"name":"p","type":"ArrayPrimitive"},
                                    {"name":"v","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"up_t","type":"DatetimePrimitive","args":[]},
                 {"name":"up_p","type":"ArrayPrimitive","args":[]},
                 {"name":"up_v","type":"ArrayPrimitive","args":[]},
                 {"name":"t","type":"DatetimePrimitive","args":[]},
                 {"name":"p","type":"ArrayPrimitive","args":[]},
                 {"name":"v","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"KinematicInterpolator","face":"up_t"},
                          "target":{"node":"up_t","face":None}},
                         {"source":{"node":"KinematicInterpolator","face":"up_p"},
                          "target":{"node":"up_p","face":None}},
                         {"source":{"node":"KinematicInterpolator","face":"up_v"},
                          "target":{"node":"up_v","face":None}},
                         {"source":{"node":"KinematicInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"p","face":None},
                          "target":{"node":"KinematicInterpolator","face":"p"}},
                         {"source":{"node":"v","face":None},
                          "target":{"node":"KinematicInterpolator","face":"v"}}],
                 "control":[]})
class KinematicInterpolator(InterpolatorPrimitive):

    def _up(self,face):
            logging.info("{0}:  Updating".\
                         format(self.name))
            
            self.t0 = self.t1
            self.p0 = self.p1
            self.v0 = self.v1
            
            self.t1 = self._data_graph.node[("up_t",)]["obj"].value
            self.p1 = self._data_graph.node[("up_p",)]["obj"].value
            self.v1 = self._data_graph.node[("up_v",)]["obj"].value
            
            logging.info("{0}:  Updated to {1}".\
                         format(self.name,self.t1))
            
            return face
    
    def _eval(self,face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("t",)]["obj"]
        p = self._data_graph.node[("p",)]["obj"]
        v = self._data_graph.node[("v",)]["obj"]
        
        dt = (t.value - self.t0).total_seconds()
        
        p.value = self.p0 + (self.v1 + self.v0) * dt / 2
        v.value = 2 * (self.p1 - self.p0) / dt - self.v0
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name,t.value))
    
        return face

@behavior(name="SplineInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"up_t","type":"DatetimePrimitive"},
                                    {"name":"up_p","type":"ArrayPrimitive"},
                                    {"name":"up_v","type":"ArrayPrimitive"},
                                    {"name":"t","type":"DatetimePrimitive"}],
                         "provide":[{"name":"p","type":"ArrayPrimitive"},
                                    {"name":"v","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"up_t","type":"DatetimePrimitive","args":[]},
                 {"name":"up_p","type":"ArrayPrimitive","args":[]},
                 {"name":"up_v","type":"ArrayPrimitive","args":[]},
                 {"name":"t","type":"DatetimePrimitive","args":[]},
                 {"name":"p","type":"ArrayPrimitive","args":[]},
                 {"name":"v","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"up_t"},
                          "target":{"node":"up_t","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"up_p"},
                          "target":{"node":"up_p","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"up_v"},
                          "target":{"node":"up_v","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"p","face":None},
                          "target":{"node":"SplineInterpolator","face":"p"}},
                         {"source":{"node":"v","face":None},
                          "target":{"node":"SplineInterpolator","face":"v"}}],
                 "control":[]})
class SplineInterpolator(InterpolatorPrimitive):
    
    def _update(self,*args,**kwargs):
        super(SplineInterpolator,self)._update(*args,**kwargs)
        
        self.h00 = Polynomial([1,0,-3,2],domain=[0,1])
        self.h01 = Polynomial([0,0,3,-2],domain=[0,1])
        self.h10 = Polynomial([0,1,-2,1],domain=[0,1])
        self.h11 = Polynomial([0,0,-1,1],domain=[0,1])

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.p0 = self.p1
        self.v0 = self.v1
        
        self.t1 = self._data_graph.node[("up_t",)]["obj"].value
        self.p1 = self._data_graph.node[("up_p",)]["obj"].value
        self.v1 = self._data_graph.node[("up_v",)]["obj"].value
        
        window = array([0,(self.t1-self.t0).total_seconds()])
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
        p = self._data_graph.node[("p",)]["obj"]
        v = self._data_graph.node[("v",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        p.value = self.p0 * self.h00(x) \
                + self.p1 * self.h01(x) \
                + self.v0 * self.h10(x) \
                + self.v1 * self.h11(x)
        
        v.value = self.p0 * self.diff_h00(x) \
                + self.p1 * self.diff_h01(x) \
                + self.v0 * self.diff_h10(x) \
                + self.v1 * self.diff_h11(x)
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name,t.value))
    
        return face
        
def install(service):
    InterpolatorPrimitive.install(service)
    KinematicInterpolator.install(service)
    SplineInterpolator.install(service)