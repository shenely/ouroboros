from math import degrees, pi, sqrt, cos, sin, tan, asin, acos, atan

from numpy import array, dot, cross
from scipy.linalg import norm
from scipy.optimize import newton
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv 

from core import Process
from util import K

__all__= ["model",
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

@Process((["mu"], [], [], [], []),#earth
         ([], ["rec"], [], ["_bar", "_t_bar"], []),#orbit
         ([], [], ["rec"], [], ["_bar"]),#apse
         ([], [], ["rec"], [], ["_bar"]))#pole
def rec2orb(mu):
    e_bar = h_bar = None
    
    while True:
        #Input/output
        r_bar, v_bar, = yield e_bar, h_bar,#position,velocity/orbital elements
        
        r = norm(r_bar)
        r_hat = r_bar / r
        
        h_bar = cross(r_bar, v_bar)#angular momentum
        e_bar = cross(v_bar, h_bar) / mu - r_hat#eccentricity

@Process(([], ["sph"], [], ["r", "az", ], []),#pqw
         ([], [], [], ["r", "az", "el"], []),#apse
         ([], [], [], ["az", "el"], []),#pole
         ([], [], ["kep"], [], ["a", "M", "e", "om", "i", "OM"]))#elements
def sph2kep():
    a = M = e = om = i = OM = None

    while True:
        r, th, e, az, el, OM, i = yield a, M, e, om, i, OM,

        a = r * (1 + e * cos(th)) / (1 - e ** 2)

        E = true2ecc(th, e)
        M = ecc2mean(E, e)

        print degrees(el), degrees(pi/2-i), sin(el), cos(i)

        om = asin(sin(el) / cos(i))
        #om = (2 * pi - om) if el < 0 else om

        i = pi / 2 - i

        OM += pi / 2

        print a, degrees(M), e, degrees(om), degrees(i), degrees(OM)