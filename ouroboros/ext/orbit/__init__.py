#!/usr/bin/env python2.7

"""Orbit library

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   07 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-03    shenely         1.0         Initial revision
2015-07-07    shenely         1.1         Added more installers

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
from sgp4.io import twoline2rv

#Internal libraries
from ouroboros.common import ObjectDict
from ouroboros.behavior import behavior,PrimitiveBehavior
#
##################


##################
# Export section #
#
__all__ = ["OrbitPrimitive",
           "KeplerOrbit",
           "SimpleOrbit"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
# 
####################


@behavior(name="OrbitPrimitive",
          type="PrimitiveBehavior")
class OrbitPrimitive(PrimitiveBehavior):pass

@behavior(name="KeplerOrbit",
          type="OrbitPrimitive",
          faces={"data":{"require":[
                                    {"name":"body",
                                     "type":"CelestialPrimitive"},
                                    {"name":"epoch",
                                     "type":"DatetimePrimitive"}],
                         "provide":[]},
                 "control":{"input":[],
                            "output":[]}},
          nodes=[{"name":"body",
                  "type":"CelestialPrimitive","args":[]},
                 {"name":"epoch",
                  "type":"DatetimePrimitive","args":[]},
                 {"name":"sma",#semi-major axis
                  "type":"NumberPrimitive","args":[]},
                 {"name":"ecc",#eccentricity
                  "type":"NumberPrimitive","args":[]},
                 {"name":"ta",#true anomaly
                  "type":"NumberPrimitive","args":[]},
                 {"name":"aop",#argument of perigee
                  "type":"NumberPrimitive","args":[]},
                 {"name":"inc",#inclination
                  "type":"NumberPrimitive","args":[]},
                 {"name":"raan",#right ascension of the ascending node
                  "type":"NumberPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"KeplerOrbit","face":"body"},
                          "target":{"node":"body","face":None}},
                         {"source":{"node":"KeplerOrbit","face":"epoch"},
                          "target":{"node":"epoch","face":None}}],
                 "control":[]})
class KeplerOrbit(OrbitPrimitive):pass
            
@behavior(name="SimpleOrbit",
          type="OrbitPrimitive",
          faces={"data":{"require":[{"name":"body",
                                     "type":"CelestialPrimitive"}],
                         "provide":[{"name":"name",
                                     "type":"StringPrimitive"}]},
                 "control":{"input":[],
                            "output":[]}},
          nodes=[{"name":"body",
                  "type":"CelestialPrimitive","args":[]},
                 {"name":"tle",
                  "type":"StringPrimitive","args":[]},
                 {"name":"name",
                  "type":"StringPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"SimpleOrbit","face":"body"},
                          "target":{"node":"body","face":None}},
                         {"source":{"node":"name","face":None},
                          "target":{"node":"SimpleOrbit","face":"name"}}],
                 "control":[]})
class SimpleOrbit(OrbitPrimitive):
    
    def _update(self,*args,**kwargs):
        super(KeplerOrbit,self)._update(*args,**kwargs)
        
        line0,line1,line2 = kwargs.get("tle").split("\n")
        
        name = self._data_graph.node[("name",)]["obj"]
        name.value = line0
        
        body = self._data_graph.node[("body",)]["obj"]
        self.value = twoline2rv(line1,line2,body.gravity)
        
def install(service):
    OrbitPrimitive.install(service)
    KeplerOrbit.install(service)
    SimpleOrbit.install(service)

    from . import body as _
    _.install(service)

    from . import interpolate as _
    _.install(service)