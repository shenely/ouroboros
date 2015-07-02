from sgp4.io import twoline2rv

from ouroboros.common import ObjectDict
from ouroboros.behavior import behavior,PrimitiveBehavior

@behavior(name="OrbitPrimitive",
          type="PrimitiveBehavior")
class OrbitPrimitive(PrimitiveBehavior):pass

@behavior(name="KeplerOrbit",
          type="OrbitPrimitive",
          faces={"data":{"require":[{"name":"epoch",
                                     "type":"DatetimePrimitive"},
                                    {"name":"body",
                                     "type":"CelestialPrimitive"}],
                         "provide":[]},
                 "control":{"input":[],
                            "output":[]}},
          nodes=[{"name":"epoch",
                  "type":"DatetimePrimitive","args":[]},
                 {"name":"body",
                  "type":"CelestialPrimitive","args":[]},
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
          edges={"data":[{"source":{"node":"KeplerOrbit","face":"epoch"},
                          "target":{"node":"epoch","face":None}},
                         {"source":{"node":"KeplerOrbit","face":"body"},
                          "target":{"node":"body","face":None}}],
                 "control":[]})
class KeplerOrbit(OrbitPrimitive):
    
    def _update(self,*args,**kwargs):
        super(KeplerOrbit,self)._update(*args,**kwargs)
        
        self.value = ObjectDict()
        self.value.sma = kwargs.get("sma")
        self.value.ecc = kwargs.get("ecc")
        self.value.ta = kwargs.get("ta")
        self.value.aop = kwargs.get("aop")
        self.value.inc = kwargs.get("inc")
        self.value.raan = kwargs.get("raan")
            
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
        body = self._data_graph.node[("body",)]["obj"]
        
        name = self._data_graph.node[("name",)]["obj"]
        name.value = line0
        
        self.value = twoline2rv(line1,line2,body.const)
        
def install(service):
    OrbitPrimitive.install(service)
    KeplerOrbit.install(service)
    SimpleOrbit.install(service)