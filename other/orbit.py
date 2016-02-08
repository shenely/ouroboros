from numpy import hstack, hsplit
from scipy.linalg import norm
from scipy.integrate import ode

from core import Process
from util import O

__all__= ["orbit", "att"]

EARTH_RADIUS = 6378.1
                       
KILO = 1000
MICRO = 1e-6

@Process((["t_dt"], ["+1*"], [], ["t_dt"], []),
         (["_bar", "_t_bar"], [], ["rec"], [], ["_bar", "_t_bar"]),
         (["mu"], [], [], [], []))
def orbit(t0_dt, r0_bar, v0_bar, mu):
    def gravity(mu):
        def gravity(t, y):
            r_bar, v_bar = hsplit(y, 2)
            
            r = norm(r_bar)
            r_hat = r_bar / r
            
            a = mu / r ** 2
            a_bar = - a * r_hat
            
            dy = hstack((v_bar, a_bar))
            
            return dy
        return gravity
    
    y = hstack((r0_bar, v0_bar))
    
    box = ode(gravity(mu))\
            .set_integrator("dopri5") \
            .set_initial_value(y, 0)
    
    r_bar,v_bar = r0_bar, v0_bar
    
    while True:
        #Input/output
        t_dt, = yield r_bar, v_bar,#time/position,velocity
        
        #Update state
        y = box.integrate((t_dt - t0_dt).total_seconds())
        r_bar, v_bar = hsplit(y, 2)

@Process(([], ["+1*"], [], ["t_dt"], []),
         (["line1", "line2"], [], ["rec"], [], ["_bar", "_t_bar"]))
def sgp4(line1, line2):
    r_bar = v_bar = None

    sat = twoline2rv(line1, line2, wgs84)

    while True:
        #Input/output
        t_dt, = yield r_bar, v_bar,#time/position,velocity

        #Update state
        r_bar, v_bar = sat.propagate(t_dt.year, t_dt.month, t_dt.day,
                                     t_dt.hour, t_dt.minute,
                                     t_dt.second + MICRO * t_dt.microsecond)
        
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