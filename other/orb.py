from numpy import array
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv 

from core import Process

__all__= ["model",
          "rec2kep", "kep2rec"]

KILO = 1000
MICRO = 1e-6

@Process(([], ["+1*"], [], ["t_dt"], []),#system
         (["line1", "line2"], [], ["rec"], [], ["_bar", "_t_bar"]))#TLE
def model(line1, line2):
    """Propagate orbit"""
    r_bar = v_bar = None

    sat = twoline2rv(line1, line2, wgs84)

    while True:
        #Input/output
        t_dt, = yield r_bar, v_bar,#time/position,velocity
        
        #Update state
        r_bar, v_bar = sat.propagate(t_dt.year, t_dt.month, t_dt.day,
                                     t_dt.hour, t_dt.minute,
                                     t_dt.second + MICRO * t_dt.microsecond)
        
        r_bar = array(r_bar)
        v_bar = array(v_bar)

def rec2kep():pass
def kep2rec():pass