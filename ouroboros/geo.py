from math import sqrt, radians, cos, sin

from numpy import array
from scipy.optimize import root

from .core import Process
from .util import I, J, K

__all__= ["model",
          "sidereal",
          "sph2geo", "geo2rec"]

def geo(R_km, f):
    def fun(x, r, el):
        lat, alt = x
        
        cos_el = cos(el)
        sin_el = sin(el)
        
        cos_lat = cos(lat)
        sin_lat = sin(lat)
        
        R_ph = R_km / sqrt(1 - (2 - f) * f * sin_lat ** 2)
        
        return array([(R_ph + alt) * cos_lat - r * cos_el,
                      ((1 - f) ** 2 * R_ph + alt) * sin_lat - r * sin_el])
        
    def jac(x, r, el):
        lat, alt = x
        
        cos_lat = cos(lat)
        sin_lat = sin(lat)
        
        R_ph = R_km / sqrt(1 - (2 - f) * f * sin_lat ** 2)
        dR_ph = - (2 - f) * f * cos_lat * sin_lat *\
                R_ph /\
                (1 - (2 - f) * f * sin_lat ** 2)
        
        return array([[dR_ph * cos_lat -\
                       (R_ph + alt) * sin_lat,
                       cos_lat],
                      [(1 - f) ** 2 * dR_ph * sin_lat +\
                       ((1 - f) ** 2 * R_ph + alt) * cos_lat,
                       sin_lat]])
    
    return fun, jac

@Process(([], ["@0"], [], [], []),
         ([], [], {"sph": True}, ["az", "az_t"], []),
         ([], [], [], [], ["_bar", "_t_bar"]))
def model():
    """Ground station"""
    az, az_t, = yield

    cos_az = cos(az)
    sin_az = sin(az)

    _hat = - sin_az * I + cos_az * J
    _t_hat = - az_t * (cos_az * I + sin_az * J)

    yield _hat, _t_hat

@Process(([], ["clock"], [], ["t_dt"], []),
         ([], [], {"rec":True}, [], ["_bar", "_t_bar"]))
def sidereal():
    """Sidereal time"""
    th_bar = 100.4606184 * K
    om_bar = radians(1.0 / 36525 + 360.98564724) / (24 * 60 * 60) * K

    while True:
        t_dt, = yield th_bar, om_bar
        
        J0 = 367 * t_dt.year \
           - (7 * (t_dt.year + (t_dt.month + 9) / 12) / 4) \
           + 275 * t_dt.month / 9 \
           + t_dt.day + 1721013.5
        UT = t_dt.hour +\
             (t_dt.minute +\
              (t_dt.second +\
               t_dt.microsecond \
               / 1e6) \
              / 60) \
             / 60
        T0 = (J0 - 2451545) / 36525
        th_G0 = 100.4606184 \
              + (36000.77004 \
                 + (0.000387933 \
                    - 2.583e-8 \
                    * T0) \
                 * T0) \
              * T0
        th_G = th_G0 + 360.98564724 * UT / 24
        
        th_G %= 360

        th_bar = radians(th_G) * K

@Process((["R_km", "f"], [], [], [], []),
         ([], ["sph"], [], ["r", "r_t",
                            "az", "az_t",
                            "el", "el_t"], []),
         ([], [], {"rec":True}, [], ["_bar", "_t_bar"]),
         ([], [], [], [], ["_bar", "_t_bar"]),
         ([], [], {"sph":True}, [], ["r", "r_t",
                                     "az", "az_t",
                                     "el", "el_t"]))
def sph2geo(R_km, f):
    """Spherical to geodetic coordinates"""
    r_bar = v_bar = _1_hat = _1_t_hat = alt = alt_t = lon = lon_t = lat = lat_t = None
    
    while True:
        r, r_t, az, az_t, el, el_t = yield r_bar, v_bar, _1_hat, _1_t_hat, alt, alt_t, lon, lon_t, lat, lat_t
        
        cos_az = cos(az)
        sin_az = sin(az)
            
        cos_el = cos(el)
        sin_el = sin(el)
        
        fun, jac = geo(R_km, f)
            
        x = array([el, r - R_km])
        lat, alt = root(fun, x, args=(r, el), jac=jac).x
        lon = az
            
        cos_lat = cos(lat)
        sin_lat = sin(lat)
        
        R_ph = R_km / sqrt(1 - (2 - f) * f * sin_lat ** 2)
        dR_ph = (2 - f) * f * cos_lat * sin_lat *\
                R_ph /\
                (1 - (2 - f) * f * sin_lat ** 2)
                
        A = cos_lat
        B = dR_ph * cos_lat - (R_ph + alt) * sin_lat
        C = sin_lat
        D = (1 - f) ** 2 * dR_ph * sin_lat +\
            ((1 - f) ** 2 * R_ph + alt) * cos_lat
        
        E = r_t * cos_el - r * el_t * sin_el
        F = r_t * sin_el + r * el_t * cos_el
        
        det = A * D - B * C
        
        alt_t = (D * E - B * F) / det
        lat_t = (A * F - C * E) / det
        lon_t = az_t
        
        R_t_ph = lat_t * dR_ph
        
        r_bar = R_ph * (cos_lat * (cos_az * I +\
                                   sin_az * J)) +\
                (1 - f) ** 2 * R_ph * sin_lat * K
        
        v_bar = R_t_ph * cos_lat * (cos_az * I +\
                                    sin_az * J) -\
                R_ph * lat_t * sin_lat * (cos_az * I +\
                                          sin_az * J) -\
                R_ph * cos_lat * az_t * (sin_az * I -\
                                         cos_az * J) +\
                (1 - f) ** 2 * (R_t_ph * sin_lat +\
                                R_ph * lat_t * cos_lat) * K
        
        _1_hat = - sin_az * I + cos_az * J
        _1_t_hat = - az_t * (cos_az * I + sin_az * J)
        
@Process((["R_km", "f"], [], [], [], []),
         ([], ["sph"], [], ["r", "r_t",
                            "az", "az_t",
                            "el", "el_t"], []),
         ([], [], {"rec":True}, [], ["_bar", "_t_bar"]))
def geo2rec(R_km, f):
    """Geodetic to rectangular coordinates"""
    r_bar = v_bar = None
    
    while True:
        alt, alt_t, lon, lon_t, lat, lat_t = yield r_bar, v_bar
        
        cos_lat = cos(lat)
        sin_lat = sin(lat)
        
        cos_lon = cos(lon)
        sin_lon = sin(lon)
        
        R_ph = R_km / sqrt(1 - (2 - f) * f * sin_lat ** 2)
        R_c = R_ph + alt
        R_s = (1 - f) ** 2 * R_ph + alt
        
        R_ph_t = lat_t *\
                 (2 - f) * f * cos_lat * sin_lat *\
                 R_ph /\
                 (1 - (2 - f) * f * sin_lat ** 2)
        R_c_t = R_ph_t + alt_t
        R_s_t = (1 - f) ** 2 * R_ph_t + alt_t
        
        r_bar = R_c * cos_lat * (cos_lon * I + sin_lon * J) +\
                R_s * sin_lat * K
        
        v_bar = (R_c_t * cos_lat -\
                  R_c * lat_t * sin_lat) *\
                (cos_lon * I + sin_lon * J) -\
                R_c * lon_t * cos_lat *\
                (sin_lon * I - cos_lon * J) +\
                (R_s_t * sin_lat +\
                 R_s * lat_t * cos_lat) * K