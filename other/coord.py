from math import radians, degrees, sqrt, cos, sin, tan, acos, asin, atan, atan2
import functools

from numpy import array, dot, einsum
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

@Process(([], ["inf"], ["equ"],
          ["alpha_deg", "delta_deg"], ["r_hat"]))
def inf2equ():
    alpha_deg, delta_deg = yield

    cos_alpha = cosd(alpha_deg)
    sin_alpha = sind(alpha_deg)
    cos_delta = cosd(delta_deg)
    sin_delta = sind(delta_deg)

    r_hat = array([cos_alpha * cos_delta,
                   sin_alpha * cos_delta,
                   sin_delta])

    yield r_hat,

@Process((["R_km", "f"], [], [], [], []),
         ([], ["geo"], ["fix"],
          ["lat_deg", "lon_deg", "alt_km"], ["r_bar"]))
def geo2fix(R_km,f):
    r_fix = O
    
    while True:
        lat_deg, lon_deg, alt_km, = yield r_fix,
        
        R_ph = R_km / sqrt(1 - (2 - f) * f * sind(lat_deg) ** 2)
        R_cos = R_ph + alt_km
        R_sin = R_ph * (1 - f) ** 2 + alt_km
        
        r_fix = array([R_cos * cosd(lat_deg) * cosd(lon_deg),
                       R_cos * cosd(lat_deg) * sind(lon_deg),
                       R_sin * sind(lat_deg)])

@Process((["R_km", "f"], [], [], [], []),
         ([], ["fix"], ["geo"],
          ["r_bar"], ["alt_km", "lat_deg", "lon_deg", "arc_km"]))
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

@Process(([], ["geo"], ["enz"],
          ["lat_deg", "lon_deg", "alt_km"], ["i", "j", "k"]))
def geo2enz():
    i, j, k = J, K, I

    while True:
        lat_deg, lon_deg, alt_km, = yield i, j, k,

        cos_lat = cosd(lat_deg)
        sin_lat = sind(lat_deg)
        cos_lon = cosd(lon_deg)
        sin_lon = sind(lon_deg)

        i = - sin_lon * I + cos_lon * J
        j = - sin_lat * (cos_lon * I + sin_lon * J) + cos_lat * K
        k = cos_lat * (cos_lon * I + sin_lon * J) + sin_lat * K

@Process(([], ["nrt"], [], ["r_bar"], []),
         ([], ["nrt"], [], ["r_bar"], []),
         ([], [], ["equ"], [], ["rho_km", "alpha_deg", "delta_deg"]))
def nrt2equ():
    rho_km = 0
    alpha_deg = 0
    delta_deg = 0

    while True:
        r_src, r_trg, = yield rho_km, alpha_deg, delta_deg,

        rho_bar = r_trg - r_src
        
        rho_km = norm(rho_bar)
        alpha_deg = degrees(atan2(rho_bar[1], rho_bar[0]))
        delta_deg = asind(rho_bar[2] / rho_km)

        print rho_km,alpha_deg,delta_deg

@Process(([], [], [], ["r_bar"], []),
         ([], [], ["nrt"], [], ["r_bar"]),
         ([], ["equ"], [], ["rho_km", "alpha_deg", "delta_deg"], []))
def equ2nrt():
    r_trg = O

    while True:
        r_src, rho_km, alpha_deg, delta_deg, = yield r_trg,

        cos_alpha = cosd(alpha_deg)
        sin_alpha = sind(alpha_deg)
        cos_delta = cosd(delta_deg)
        sin_delta = sind(delta_deg)
        
        rho_bar = rho_km * array([cos_alpha * cos_delta,
                                  sin_alpha * cos_delta,
                                  sin_delta])

        r_trg = rho_bar + r_src

@Process(([], [], [], ["i", "j", "k"], []),
         ([], ["nrt"], [], ["r_bar"], []),
         ([], [], ["fix"], [], ["r_bar"]))
def nrt2fix():
    r_fix = O

    while True:
        i, j, k, r_bar, = yield r_fix,

        r_fix = array([dot(r_bar, i),
                       dot(r_bar, j),
                       dot(r_bar, k)])

@Process(([], [], [], ["i", "j", "k"], []),
         ([], [], ["nrt"], [], ["r_bar"]),
         ([], ["fix"], [], ["r_bar"], []))
def fix2nrt():
    r_bar = O

    while True:
        i, j, k, r_fix, = yield r_bar,

        r_bar = r_fix[0] * i + r_fix[1] * j + r_fix[2] * k