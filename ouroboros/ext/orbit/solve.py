from math import sqrt,cos,sin,tan,atan

from numpy import matrix
from scipy.optimize import newton
from sgp4.ext import newtonnu

from ouroboros.behavior import behavior
from ouroboros.lib import ActionPrimitive

KEPLER_EQUATION = lambda E,M,e:E - e * sin(E) - M#Kepler equation
KEPLER_DERIVATIVE = lambda E,M,e:1 - e * cos(E)#Derivative of Kepler equation
ANOMALY_ERROR = 1e-15#Acceptable error in mean anomaly

#Rotation matrices
ROTATION_X_AXIS = lambda th:matrix([[1,0,0],
                                    [0,cos(th),-sin(th)],
                                    [0,sin(th),cos(th)]])
ROTATION_Y_AXIS = lambda th:matrix([[cos(th),0,sin(th)],
                                    [0,1,0],
                                    [-sin(th),0,cos(th)]])
ROTATION_Z_AXIS = lambda th:matrix([[cos(th),-sin(th),0],
                                    [sin(th),cos(th),0],
                                    [0,0,1]])

class OrbitPropagator(ActionPrimitive):pass

class KeplerPropagator(ActionPrimitive):
    
    def _execute(self):
        orbit = self._data_graph.node[("orbit",)]["obj"]
        
        epoch = orbit._data_graph.node[("epoch",)]["obj"]
        sma = orbit._data_graph.node[("sma",)]["obj"]
        ecc = orbit._data_graph.node[("ecc",)]["obj"]
        ta = orbit._data_graph.node[("ecc",)]["obj"]
        aop = orbit._data_graph.node[("ta",)]["obj"]
        inc = orbit._data_graph.node[("inc",)]["obj"]
        raan = orbit._data_graph.node[("raan",)]["obj"]
        
        body = self._data_graph.node[("orbit",)]["obj"]
        
        t0 = epoch.value
        a = sma.value
        e = ecc.value
        th = ta.value
        om = aop.value
        i = inc.value
        OM = raan.value
        
        E,M = newtonnu(e,th)
        
        t = self._data_graph.node[("t",)]["obj"].value
        mu = body.gravity["mu"]
        n = sqrt(mu / a ** 3)
        
        M = n * (t - t0).total_seconds()
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,e),ANOMALY_ERROR)
        th = atan(sqrt((1 + e) / (1 - e)) * tan(E / 2))
        
        epoch.value = t
        ta.value = th
        
    
class SimplePropagator(ActionPrimitive):pass
class EphemerisPropagator(ActionPrimitive):pass