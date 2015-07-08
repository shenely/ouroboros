from math import sqrt,cos,sin
import logging

from ouroboros.behavior import behavior
from ouroboros.lib import ActionPrimitive
from ouroboros.lib.watch import WatcherPrimitive

@behavior(name="EphemerisPrimitive",
          type="ActionPrimitive")
class EphemerisPrimitive(ActionPrimitive,WatcherPrimitive):pass

@behavior(name="CircularEphemeris",
          type="ActionPrimitive",
          faces={"data":{"require":[{"name":"body","type":"CelestialPrimitive"},
                                    {"name":"epoch","type":"DatetimePrimitive"},
                                    {"name":"time","type":"DatetimePrimitive"}],
                         "provide":[{"name":"position","type":"VectorPrimitive"},
                                    {"name":"velocity","type":"VectorPrimitive"}]},
                 "control":{"input":[],
                            "output":[]}},
          nodes=[{"name":"body","type":"CelestialPrimitive","args":[]},
                 {"name":"epoch","type":"DatetimePrimitive","args":[]},
                 {"name":"radius","type":"NumberPrimitive","args":[]},
                 {"name":"phase","type":"NumberPrimitive","args":[]},
                 {"name":"time","type":"DatetimePrimitive","args":[]}],
          edges={"data":[{"source":{"node":"CircularEphemeris","face":"body"},
                          "target":{"node":"body","face":None}},
                         {"source":{"node":"CircularEphemeris","face":"epoch"},
                          "target":{"node":"epoch","face":None}},
                         {"source":{"node":"CircularEphemeris","face":"time"},
                          "target":{"node":"time","face":None}},
                         {"source":{"node":"position","face":None},
                          "target":{"node":"CircularEphemeris","face":"position"}},
                         {"source":{"node":"velocity","face":None},
                          "target":{"node":"CircularEphemeris","face":"velocity"}}],
                 "control":[]})
class CircularEphemeris(EphemerisPrimitive):
           
    def _execute(self):
        body = self._data_graph.node[("body",)]["obj"]
        
        t0 = self._data_graph.node[("epoch",)]["obj"].value
        R = self._data_graph.node[("radius",)]["obj"].value
        th0 = self._data_graph.node[("phase",)]["obj"].value
        
        t1 = self._data_graph.node[("time",)]["obj"].value
        
        mu = body.gravity.mu
        
        n = sqrt(mu / R ** 3)
        th1 = th0 + n * (t1 - t0).total_seconds()
        
        logging.info("{0}:  Propagating".\
                     format(self.name))
        
        p = self._data_graph.node[("position",)]["obj"].value
        p[0] = R * cos(th1)
        p[1] = R * sin(th1)
        p[2] = 0
        
        v = self._data_graph.node[("velocity",)]["obj"].value
        v[0] = - n * R * sin(th1)
        v[1] = n * R * cos(th1)
        v[2] = 0
        
        logging.info("{0}:  Propagated to {1}".\
                     format(self.name,t1))

@behavior(name="OrbitalEphemeris",
          type="PrimitiveBehavior")
class OrbitalEphemeris(EphemerisPrimitive):pass

@behavior(name="DevelopmentEphemeris",
          type="PrimitiveBehavior")
class DevelopmentEphemeris(EphemerisPrimitive):pass