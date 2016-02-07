from math import sqrt, cos, sin, asin, atan2

from numpy import array, dot, cross
from scipy.linalg import norm

from core import Process

__all__= ["abs2rel", "rel2abs", 
          "nrt2rot", "rot2nrt", 
          "fun2obl", "obl2fun", 
          "rec2sph", "sph2rec"]

@Process(([], [], [], ["_bar", "_t_bar"], []),
         ([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]))
def abs2rel():
    """Absolute to relative origin"""
    _bar = _t_bar = None
    
    while True:
        _1_bar, _1_t_bar, _2_bar, _2_t_bar, = yield _bar, _t_bar,
        
        _bar = _2_bar - _1_bar
        _t_bar = _2_t_bar - _1_t_bar
    
@Process(([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]),
         ([], ["rec"], [], ["_bar", "_t_bar"], []))
def rel2abs():
    """Relative to absolute origin"""
    _2_bar = _2_t_bar = None
    
    while True:
        _1_bar, _1_t_bar, _bar, _t_bar, = yield _2_bar, _2_t_bar,
        
        _2_bar = _bar + _1_bar
        _2_t_bar = _t_bar + _1_t_bar

@Process(([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]))
def nrt2rot():
    """Inertial to rotating frame"""
    _bar = _t_bar = None
    
    while True:
        th_bar, om_bar, _bar, _t_bar, = yield _bar, _t_bar,
        
        th = norm(th_bar)
        th_hat = th_bar / th
        
        cos_th = cos(th)
        sin_th = sin(th)
        
        th_t = dot(th_bar, om_bar) / th
        th_t_hat = (th * om_bar - th_t * th_bar) / th ** 2
        
        dot_th = dot(th_hat, _bar)
        cross_th = cross(th_hat, _bar)

        _t_bar = cos_th * _t_bar +\
                sin_th * cross(th_hat, _t_bar) +\
                (1 - cos_th) * dot(th_hat, _t_bar) * th_hat - \
                \
                th_t * (sin_th * _bar -\
                        cos_th * cross_th -\
                        sin_th * dot_th * th_hat) +\
                \
                sin_th * cross(th_t_hat, _bar) +\
                (1 - cos_th) * (dot(th_t_hat, _bar) * th_hat +\
                                dot_th * th_t_hat)

        _bar = cos_th * _bar +\
               sin_th * cross_th +\
               (1 - cos_th) * dot_th * th_hat
            
@Process(([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]),
         ([], ["rec"], [], ["_bar", "_t_bar"], []))
def rot2nrt(th_bar, r_bar):
    """Rotating to inertial frame"""
    _bar = _t_bar = None
    
    while True:
        th_bar, om_bar, _bar, _t_bar, = yield _bar, _t_bar,
        
        th = norm(th_bar)
        th_hat = th_bar / th
        
        cos_th = cos(th)
        sin_th = sin(th)
        
        th_t = dot(th_bar, om_bar) / th
        th_t_hat = (th * om_bar - th_t * th_bar) / th ** 2
        
        dot_th = dot(th_hat, _bar)
        cross_th = cross(th_hat, _bar)

        _t_bar = cos_th * _t_bar -\
                sin_th * cross(th_hat, _t_bar) +\
                (1 - cos_th) * dot(th_hat, _t_bar) * th_hat - \
                \
                th_t * (sin_th * _bar +\
                        cos_th * cross_th -\
                        sin_th * dot_th * th_hat) -\
                \
                sin_th * cross(th_t_hat, _bar) -\
                (1 - cos_th) * (dot(th_t_hat, _bar) * th_hat -\
                                dot_th * th_t_hat)

        _bar = cos_th * _bar -\
               sin_th * cross_th +\
               (1 - cos_th) * dot_th * th_hat
    
@Process(([], [], [], ["_bar", "_t_bar"], []),
         ([], [], [], ["_bar", "_t_bar"], []),
         ([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]))
def fun2obl():
    """Fundamental to oblique plane"""
    _bar = _t_bar = None
    
    while True:
        _1_bar, _1_t_bar, _3_bar, _3_t_bar, _bar, _t_bar = yield _bar, _t_bar,
        
        _2_bar = cross(_3_bar, _1_bar)
        
        _1 = norm(_1_bar)
        i_hat = _1_bar / _1
        
        _2 = norm(_2_bar)
        j_hat = _2_bar / _2
        
        k_hat = cross(i_hat, j_hat)
        
        _1_t = dot(_1_bar, _1_t_bar) / _1
        i_t_hat = (_1 * _1_t_bar - _1_t * _1_bar) / _1 ** 2
        
        _2_t_bar = cross(_3_t_bar, _1_bar) +\
                   cross(_3_bar, _1_t_bar)
        
        _2_t = dot(_2_bar, _2_t_bar) / _2
        j_t_hat = (_2 * _2_t_bar - _2_t * _2_bar) / _2 ** 2
        
        k_t_hat = cross(i_t_hat, j_hat) + \
                  cross(i_hat, j_t_hat)
    
        _t_bar = array([dot(_t_bar, i_hat),
                        dot(_t_bar, j_hat),
                        dot(_t_bar, k_hat)])
    
        _t_bar += array([dot(_bar, i_t_hat),
                         dot(_bar, j_t_hat),
                         dot(_bar, k_t_hat)])
    
        _bar = array([dot(_bar, i_hat),
                      dot(_bar, j_hat),
                      dot(_bar, k_hat)])
    
@Process(([], [], [], ["_bar", "_t_bar"], []),
         ([], ["rec"], [], ["_bar", "_t_bar"], []),
         ([], [], ["rec"], [], ["_bar", "_t_bar"]),
         ([], ["rec"], [], ["_bar", "_t_bar"], []))
def obl2fun():
    """Oblique to fundamental plane"""
    _bar = _t_bar = None
    
    while True:
        _1_bar, _1_t_bar, _3_bar, _3_t_bar, _bar, _t_bar = yield _bar, _t_bar,
        
        _2_bar = cross(_3_bar, _1_bar)
        
        _1 = norm(_1_bar)
        i_hat = _1_bar / _1
        
        _2 = norm(_2_bar)
        j_hat = _2_bar / _2
        
        k_hat = cross(i_hat, j_hat)
        
        _1_t = dot(_1_bar, _1_t_bar) / _1
        i_t_hat = (_1 * _1_t_bar - _1_t * _1_bar) / _1 ** 2
        
        _2_t_bar = cross(_3_t_bar, _1_bar) +\
                   cross(_3_bar, _1_t_bar)
        
        _2_t = dot(_2_bar, _2_t_bar) / _2
        j_t_hat = (_2 * _2_t_bar - _2_t * _2_bar) / _2 ** 2
        
        k_t_hat = cross(i_t_hat, j_hat) + \
                  cross(i_hat, j_t_hat)
    
        _t_bar = _t_bar[0] * i_hat + \
                 _t_bar[1] * j_hat + \
                 _t_bar[2] * k_hat
    
        _t_bar -= _bar[0] * i_t_hat + \
                  _bar[1] * j_t_hat + \
                  _bar[2] * k_t_hat
    
        _bar = _bar[0] * i_hat + \
               _bar[1] * j_hat + \
               _bar[2] * k_hat
           
@Process(([], ["rec"], ["sph"],
          ["_bar", "_t_bar"], 
          ["r", "r_t", "az", "az_t", "el", "el_t"]))    
def rec2sph():
    """Rectangular to spherical coordinates"""
    r = r_t = az = az_t = el = el_t = None
    
    while True:
        r_bar, v_bar = yield r, r_t, az, az_t, el, el_t,
        
        x, y, z = r_bar
        x_t, y_t, z_t = v_bar
        
        r = norm(r_bar)
        r_t = dot(r_bar, v_bar) / r
        
        xy__2 = r ** 2 - z ** 2
        
        az = atan2(y,  x)
        az_t = (x * y_t - y * x_t) / xy__2
        
        el = asin(z / r)
        el_t = (z_t - (r_t / r) * z) / sqrt(xy__2)
        
        print r, az, el
               
@Process(([], ["sph"], ["rec"],
          ["r", "r_t", "az", "az_t", "el", "el_t"],
          ["_bar", "_t_bar"]))   
def sph2rec():
    """Spherical to rectangular coordinates"""
    r_bar = v_bar = None
    
    while True:
        r, r_t, az, az_t, el, el_t, = yield r_bar, v_bar
        
        cos_az = cos(az)
        sin_az = sin(az)
        
        cos_el = cos(el)
        sin_el = sin(el)
        
        x = r * cos_az * cos_el
        y = r * sin_az * cos_el
        z = r * sin_el
        
        r_bar = array([x, y, z])
        
        x_t = r_t * cos_az * cos_el -\
              r * az_t * sin_az * cos_el -\
              r * el_t * cos_az * sin_el
        y_t = r_t * sin_az * cos_el +\
              r * az_t * cos_az * cos_el -\
              r * el_t * sin_az * sin_el
        z_t = r_t * sin_el +\
              r * el_t * cos_el
        
        v_bar = array([x_t, y_t, z_t])
        