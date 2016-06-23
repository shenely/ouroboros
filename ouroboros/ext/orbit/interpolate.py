#!/usr/bin/env python2.7

"""Interpolator functions

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision
2015-07-25    shenely         1.1         Added new (Hermite) interpolators
2016-06-18    shenely         1.2         General code cleanup
2016-06-22    shenely         1.3         Refactoring directories

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries
import numpy
import numpy.polynomial

#Internal libraries
from ...behavior import behavior, PrimitiveBehavior
from ...lib.watch import WatcherPrimitive
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
__version__ = "1.3"#current version [major.minor]
# 
####################


@behavior(name="InterpolatorPrimitive",
          type="PrimitiveBehavior")
class InterpolatorPrimitive(PrimitiveBehavior, WatcherPrimitive):

    def _process(self, face):
        return self._up(face) \
            if face == "up" else \
            self._eval(face)
    
@behavior(name="LinearInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"point","type":"DatetimePrimitive"},
                                    {"name":"value","type":"ArrayPrimitive"},
                                    {"name":"x","type":"DatetimePrimitive"}],
                         "provide":[{"name":"y","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"point","type":"DatetimePrimitive","args":[]},
                 {"name":"value","type":"ArrayPrimitive","args":[]},
                 {"name":"x","type":"DatetimePrimitive","args":[]},
                 {"name":"y","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"point"},
                          "target":{"node":"point","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"value"},
                          "target":{"node":"value","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"x"},
                          "target":{"node":"x","face":None}},
                         {"source":{"node":"y","face":None},
                          "target":{"node":"SplineInterpolator","face":"y"}}],
                 "control":[]})
class LinearInterpolator(InterpolatorPrimitive):
    
    def init(self, *args, **kwargs):
        super(LinearInterpolator, self).init(*args, **kwargs)
        
        self.h00 = numpy.polynomial.Polynomial([1, -1], domain=[0, 1])
        self.h01 = numpy.polynomial.Polynomial([0, 1], domain=[0, 1])

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.x0 = self.x1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("point",)]["obj"].value
        self.a1 = self._data_graph.node[("value",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = numpy.array([0, self.dt])
        self.h00.convert(window=window)
        self.h01.convert(window=window)
        
        logging.info("{0}:  Updated to {1}".\
                     format(self.name, self.t1))
        
        return face
    
    def _eval(self, face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("x",)]["obj"]
        a = self._data_graph.node[("y",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        a.value = self.a0 * self.h00(x) \
                + self.a1 * self.h01(x)
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name, t.value))
    
        return face

@behavior(name="CubicInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"point","type":"DatetimePrimitive"},
                                    {"name":"value","type":"ArrayPrimitive"},
                                    {"name":"slope","type":"ArrayPrimitive"},
                                    {"name":"x","type":"DatetimePrimitive"}],
                         "provide":[{"name":"y","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"point","type":"DatetimePrimitive","args":[]},
                 {"name":"value","type":"ArrayPrimitive","args":[]},
                 {"name":"slope","type":"ArrayPrimitive","args":[]},
                 {"name":"x","type":"DatetimePrimitive","args":[]},
                 {"name":"y","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"point"},
                          "target":{"node":"point","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"value"},
                          "target":{"node":"value","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"slope"},
                          "target":{"node":"slope","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"x"},
                          "target":{"node":"x","face":None}},
                         {"source":{"node":"y","face":None},
                          "target":{"node":"SplineInterpolator","face":"y"}}],
                 "control":[]})
class CubicInterpolator(InterpolatorPrimitive):
    
    def _update(self, *args, **kwargs):
        super(CubicInterpolator, self)._update(*args, **kwargs)
        
        self.h00 = numpy.polynomial.Polynomial([1, 0, -3, 2], domain=[0, 1])
        self.h01 = numpy.polynomial.Polynomial([0, 0, 3, -2], domain=[0, 1])
        self.h10 = numpy.polynomial.Polynomial([0, 1, -2, 1], domain=[0, 1])
        self.h11 = numpy.polynomial.Polynomial([0, 0, -1, 1], domain=[0, 1])

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.v0 = self.v1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("point",)]["obj"].value
        self.v1 = self._data_graph.node[("value",)]["obj"].value
        self.a1 = self._data_graph.node[("slope",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = numpy.array([0, self.dt])
        self.h00.convert(window=window)
        self.h01.convert(window=window)
        self.h10.convert(window=window)
        self.h11.convert(window=window)
        
        logging.info("{0}:  Updated to {1}".\
                     format(self.name, self.t1))
        
        return face
    
    def _eval(self, face):
        logging.info("{0}:  Evaluating".\
                     format(self.name))
        
        t = self._data_graph.node[("x",)]["obj"]
        v = self._data_graph.node[("y",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        v.value = self.v0 * self.h00(x) \
                + self.v1 * self.h01(x) \
                + self.a0 * self.h10(x) * self.dt \
                + self.a1 * self.h11(x) * self.dt
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name, t.value))
    
        return face

@behavior(name="QuinticInterpolator",
          type="InterpolatorPrimitive",
          faces={"data":{"require":[{"name":"point","type":"DatetimePrimitive"},
                                    {"name":"value","type":"ArrayPrimitive"},
                                    {"name":"slope","type":"ArrayPrimitive"},
                                    {"name":"curve","type":"ArrayPrimitive"},
                                    {"name":"x","type":"DatetimePrimitive"}],
                         "provide":[{"name":"y","type":"ArrayPrimitive"}]},
                 "control":{"input":["up","in"],
                            "output":["up","out"]}},
          nodes=[{"name":"point","type":"DatetimePrimitive","args":[]},
                 {"name":"value","type":"ArrayPrimitive","args":[]},
                 {"name":"slope","type":"ArrayPrimitive","args":[]},
                 {"name":"curve","type":"ArrayPrimitive","args":[]},
                 {"name":"x","type":"DatetimePrimitive","args":[]},
                 {"name":"y","type":"ArrayPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SplineInterpolator","face":"point"},
                          "target":{"node":"point","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"value"},
                          "target":{"node":"value","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"slope"},
                          "target":{"node":"slope","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"curve"},
                          "target":{"node":"curve","face":None}},
                         {"source":{"node":"SplineInterpolator","face":"t"},
                          "target":{"node":"t","face":None}},
                         {"source":{"node":"p","face":None},
                          "target":{"node":"SplineInterpolator","face":"p"}}],
                 "control":[]})
class QuinticInterpolator(InterpolatorPrimitive):
    
    def _update(self, *args, **kwargs):
        super(QuinticInterpolator, self)._update(*args, **kwargs)
        
        self.h00 = numpy.polynomial.Polynomial([1, 0, 0, -10, 15, -6], domain=[0, 1])
        self.h01 = numpy.polynomial.Polynomial([0, 0, 0, 10, -15, 6], domain=[0, 1])
        self.h10 = numpy.polynomial.Polynomial([0, 1, 0, -6, 8, -3], domain=[0, 1])
        self.h11 = numpy.polynomial.Polynomial([0, 0, 0, -4, 7, -3], domain=[0, 1])
        self.h20 = numpy.polynomial.Polynomial([0, 0, 1, -3, 3, -1], domain=[0, 1]) / 2
        self.h21 = numpy.polynomial.Polynomial([0, 0, 0, 1, -2, 1], domain=[0, 1]) / 2

    def _up(self,face):
        logging.info("{0}:  Updating".\
                     format(self.name))
        
        self.t0 = self.t1
        self.p0 = self.p1
        self.v0 = self.v1
        self.a0 = self.a1
        
        self.t1 = self._data_graph.node[("point",)]["obj"].value
        self.p1 = self._data_graph.node[("value",)]["obj"].value
        self.v1 = self._data_graph.node[("slope",)]["obj"].value
        self.a1 = self._data_graph.node[("curve",)]["obj"].value
        self.dt = (self.t1.value - self.t0).total_seconds()
        
        window = numpy.array([0, self.dt])
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
        
        t = self._data_graph.node[("x",)]["obj"]
        p = self._data_graph.node[("y",)]["obj"]
        
        x = (t.value - self.t0).total_seconds()
        
        p.value = self.p0 * self.h00(x) \
                + self.p1 * self.h01(x) \
                + self.v0 * self.h10(x) * self.dt \
                + self.v1 * self.h11(x) * self.dt \
                + self.a0 * self.h20(x) * self.dt ** 2 \
                + self.a1 * self.h21(x) * self.dt ** 2
        
        logging.info("{0}:  Evaluated at {1}".\
                     format(self.name, t.value))
    
        return face
        
def install(service):
    InterpolatorPrimitive.install(service)
    LinearInterpolator.install(service)
    CubicInterpolator.install(service)
    QuinticInterpolator.install(service)