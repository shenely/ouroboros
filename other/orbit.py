from numpy import array, hstack, hsplit
from scipy.integrate import ode
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv 

from core import Process
from util import O

__all__= ["orbit", "att"]

KILO = 1000
MICRO = 1e-6

@Process(([], ["+1*"], [], ["t_dt"], []),#system
         (["line1", "line2"], [], ["rec"], [], ["_bar", "_t_bar"]))#TLE
def orbit(line1, line2):
    """Propagate orbit
    
    Arguments:
    - (Zeroth line of TLE)
    - First line of TLE
    - Second line of TLE
    
    Inputs:
    - Every 1 tick
    
    Outputs:
    - Rectangular
    
    Requires:
    - Current date/time
    
    Provides:
    - Position/velocity
    """
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
        
@Process((["t_dt"], ["+1*"], [], ["t_dt"], []),
         (["_bar", "_t_bar"], [], ["rec"], [], ["_bar", "_t_bar"]))
def att(t0_dt, th0_bar, om0_bar):
    def rigid(t,y):
        th_bar, om_bar = hsplit(y, 2)
        
        dy = hstack((om_bar, O))
        
        return dy
    
    y = hstack((th0_bar,om0_bar))
    
    box = ode(rigid)\
            .set_integrator("dopri5") \
            .set_initial_value(y, 0)
    
    th_bar, om_bar = th0_bar, om0_bar
    
    while True:
        #Input/output
        t_dt, = yield th_bar, om_bar,#time/position,velocity
        
        #Update state
        y = box.integrate((t_dt - t0_dt).total_seconds())
        th_bar, om_bar = hsplit(y, 2)