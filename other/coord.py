from math import radians, degrees, sqrt, cos, sin, tan, acos, asin, atan, atan2
import functools

from numpy import array, matrix
from scipy.linalg import norm

from core import Process

__all__= ["inf2equ",
          "geo2fix", "fix2geo", 
          "nrt2equ", "equ2nrt", 
          "nrt2fix", "fix2nrt"]

#Unit vectors
O = array([0,0,0])
I = array([1,0,0])
J = array([0,1,0])
K = array([0,0,1])
                       
#Wrapper functions for angles in degrees
@functools.wraps(cos)
def cosd(x):return cos(radians(x))

@functools.wraps(sin)
def sind(x):return sin(radians(x))

@functools.wraps(tan)
def tand(x):return tan(radians(x))

@functools.wraps(acos)
def acosd(x):return degrees(acos(x))

@functools.wraps(asin)
def asind(x):return degrees(asin(x))

@functools.wraps(atan)
def atand(x):return degrees(atan(x))

@Process(([], ["+0"], ["inf2equ"], 
          ["alpha_deg", "delta_deg"], ["r_hat"]))
def inf2equ():
    alpha_deg, delta_deg = yield
    
    r_hat = matrix([cosd(delta_deg) * cosd(alpha_deg),
                    cosd(delta_deg) * sind(alpha_deg),
                    sind(delta_deg)]).T
                    
    yield r_hat,

@Process((["R_km", "f"], [], [], [], []),
         ([], [], ["geo2fix"], 
          ["lat_deg", "lon_deg", "alt_km"], ["r_fix"]))
def geo2fix(R_km,f):
    r_fix = O
    
    while True:
        lat_deg, lon_deg, alt_km, = yield r_fix,
        
        R_ph = R_km / sqrt(1 - (2 * f - f ** 2) * sind(lat_deg) ** 2)
        R_cos = R_ph + alt_km
        R_sin = R_ph * (1 - f) ** 2 + alt_km
        
        r_fix = array([R_cos * cosd(lat_deg) * cosd(lon_deg),
                       R_cos * cosd(lat_deg) * sind(lon_deg),
                       R_sin * sind(lat_deg)])

@Process((["R_km", "f"], [], [], [], []),
         ([], [], ["fix2geo"],
          ["r_fix"], ["alt_km", "lat_deg", "lon_deg", "arc_km"]))
def fix2geo(R_km, f):
    alt_km = 0
    lat_deg = 0
    lon_deg = 0
    
    arc_km = 0

    while True:
        r_fix, = yield alt_km, lat_deg, lon_deg, arc_km

        r = norm(r_fix)

        alt_km = r - R_km
        lon_deg = degrees(atan2(r_fix[1], r_fix[0]))
        lat_deg = atand(tand(asind(r_fix[2] / r)) / (1 - f ** 2))
        
        arc_km = acosd(R_km / r)

@Process(([], [], [], ["r_bar"], []),
         ([], [], [], ["r_bar"], []),
         ([], [], ["nrt2equ"],
          [], ["rho_km", "alpha_deg", "delta_deg"]))
def nrt2equ():
    rho_km = 0
    alpha_deg = 0
    delta_deg = 0

    while True:
        r1, r2, = yield rho_km, alpha_deg, delta_deg,

        rho_bar = r2 - r1
        
        rho_km = norm(rho_bar)
        alpha_deg = degrees(atan2(rho_bar[1], rho_bar[0]))
        delta_deg = asind(rho_bar[2] / rho_km)

@Process(([], [], [], ["r_bar"], []),
         ([], [], [], [], ["r_bar"]),
         ([], [], ["equ2nrt"],
          ["rho_km", "alpha_deg", "delta_deg"], []))
def equ2nrt():
    r2 = O

    while True:
        r1, rho_km, alpha_deg, delta_deg, = yield r2,
        
        rho_bar = rho_km * array([cosd(alpha_deg) * cosd(delta_deg),
                                  sind(alpha_deg) * cosd(delta_deg),
                                  sind(delta_deg)])

        r2 = rho_bar + r1

@Process(([], [], [], ["th_G"], []),
         ([], [], [], ["r_bar"], []),
         ([], [], ["nrt2fix"], [], ["r_fix"]))
def nrt2fix():
    r_fix = O

    while True:
        th_G, r_bar, = yield r_fix,

        r_fix = array([r_bar[0] * cosd(th_G) + r_bar[1] * sind(th_G),
                       - r_bar[0] * sind(th_G) + r_bar[1] * cosd(th_G),
                       r_bar[2]])

@Process(([], [], [], ["th_G"], []),
         ([], [], [], [], ["r_bar"]),
         ([], [], ["fix2nrt"], ["r_fix"], []))
def fix2nrt():
    r_bar = O

    while True:
        th_G, r_fix, = yield r_bar,

        r_bar = array([r_fix[0] * cosd(th_G) - r_fix[1] * sind(th_G),
                       r_fix[0] * sind(th_G) + r_fix[1] * cosd(th_G),
                       r_fix[2]])