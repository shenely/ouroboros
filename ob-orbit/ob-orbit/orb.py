from math import pi, sqrt, cos, sin, tan, asin, atan

from numpy import array, cross, hstack, hsplit
from scipy.linalg import norm
from scipy.optimize import newton
from scipy.integrate import ode
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv 

from ..core import Process

__all__= ["model", "simple",
          "rec2orb", "sph2kep"]

KILO = 1000
MICRO = 1e-6

def true2ecc(th_rad, e):
    E_rad = 2 * atan(sqrt((1 - e) / (1 + e)) * tan(th_rad / 2))
    
    return E_rad

def ecc2true(E_rad, e):
    th_rad = 2 * atan(sqrt((1 + e) / (1 - e)) * tan(E_rad / 2))
    
    return th_rad

def ecc2mean(E_rad, e):
    M_rad = E_rad - e * sin(E_rad)
    
    return M_rad

def mean2ecc(M_rad, e):
    E_rad = newton(lambda E, M, e: E - e * sin(E) - M, M_rad,
                   fprime=lambda E, M, e: 1 - e * cos(E),
                   tol=1e-12)
    
    return E_rad

@Process("orb.model",
         (["t_dt"], ["tick"], [], ["t_dt"], []),#system
         (["_bar", "_t_bar"], [], {"rec":True}, [], ["_bar", "_t_bar"]),#sat
         (["mu"], [], [], [], []))#earth
def model(t0_dt, r0_bar, v0_bar, mu):
    """Propagate orbit"""

    def kepler(t, y):
        r_bar, v_bar = hsplit(y, 2)

        r = norm(r_bar)

        dy = hstack((v_bar, - mu * r_bar / r ** 3))

        return dy

    y = hstack((r0_bar,r0_bar))

    box = ode(kepler)\
            .set_integrator("dopri5") \
            .set_initial_value(y, 0)

    r_bar, v_bar = r0_bar, v0_bar

    while True:
        #Input/output
        t_dt, = yield r_bar, v_bar,#time/position,velocity

        #Update state
        y = box.integrate((t_dt - t0_dt).total_seconds())
        r_bar, v_bar = hsplit(y, 2)

@Process("orb.simple",
         ([], ["tick"], [], ["t_dt"], []),#clock
         (["line1", "line2"], [], {"rec":True}, [], ["_bar", "_t_bar"]))#TLE
def simple(line1, line2):
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

@Process("orb.rec2orb",
         (["mu"], [], [], [], []),#earth
         ([], ["rec"], [], ["_bar", "_t_bar"], []),#orbit
         ([], [], {"rec":True}, [], ["_bar"]),#apse
         ([], [], {"rec":True}, [], ["_bar"]))#pole
def rec2orb(mu):
    e_bar = h_bar = None
    
    while True:
        #Input/output
        r_bar, v_bar, = yield e_bar, h_bar,#position,velocity/orbital elements
        
        r = norm(r_bar)
        r_hat = r_bar / r
        
        h_bar = cross(r_bar, v_bar)#angular momentum
        e_bar = cross(v_bar, h_bar) / mu - r_hat#eccentricity

@Process("orb.sph2kep",
         ([], ["sph"], [], ["r", "az", ], []),#pqw
         ([], [], [], ["r", "az", "el"], []),#apse
         ([], [], [], ["az", "el"], []),#pole
         ([], [], {"kep":True}, [], ["a", "M", "e", "om", "i", "OM"]))#elements
def sph2kep():
    a = M = e = om = i = OM = None

    while True:
        #Input/output
        r, th, e, az, el, OM, i = yield a, M, e, om, i, OM,

        #Semi-major axis
        a = r * (1 + e * cos(th)) / (1 - e ** 2)#from orbit equation

        #True anomaly to...
        E = true2ecc(th, e)#...eccentric anonaly
        M = ecc2mean(E, e)#...mean anomaly

        #Argument of periapsis
        om = asin(sin(el) / cos(i))#from eccentricity vector
        om = (pi - om) if pi / 2 < az < 3 * pi / 2 else om

        #Inclination
        i = pi / 2 - i#from angular momentum elevation

        #Right ascension of the ascending node
        OM += pi / 2#from angular momentum azimuth
        
        print a, M, e, om, i, OM
