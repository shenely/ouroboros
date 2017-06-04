#built-in libraries
from math import cos, sin, asin, atan2

#external libraries
from numpy import ndarray, array, dot, cross
from scipy.linalg import norm

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__= ["abs2rel", "rel2abs", 
          "nrt2rot", "rot2nrt", 
          "fun2obl", "obl2fun", 
          "rec2sph", "sph2rec"]

@PROCESS('vec.abs2rel', NORMAL,
         Item('source',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros()),
         Item('target',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('relative',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def abs2rel(_1, _2, _3):
    """Absolute to relative origin"""
    _1, _2, _3 = yield
    while True:
        (_1_bar, _1_t_bar), (rec1,) = _1.next()
        rec3 = (_ for ((), (_,)) in _3)
        _3 = (((_2_bar - _1_bar, _2_t_bar - _1_t_bar)
                if (rec1 and rec2) ^ rec3.next()
                else (None, None)),
               (rec1 and rec2,))
              for (_2_bar, _2_t_bar), (rec2,) in _2)
        _1, _2, _3 = yield None, None, _3
    
@PROCESS('vec.rel2abs', NORMAL,
         Item('source',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('target',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('relative',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rel2abs(_1, _2, _3):
    """Relative to absolute origin"""
    _1, _2, _3 = yield
    while True:
        (_1_bar, _1_t_bar), (rec1,) = _1.next()
        rec2 = (_ for ((), (_,)) in _2)
        _2 = ((((_3_bar + _3_1_bar, _t_bar + _1_t_bar)
                if (rec1 and rec3) ^ rec2.next()
                else (None, None)),
               (rec1 and rec3,))
              for (_3_bar, _3_t_bar), (rec,) in _3)
        _1, _2, _3 = yield None, _2, None
    
@PROCESS('vec.nrt2rot', NORMAL,
         Item('axis',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('inertial',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('rotating',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def nrt2rot(_, _1, _2):
    """Inertial to rotating frame"""
    _, _1, _2 = yield
    while True:
        (_bar, _t_bar), (rec,) = _.next()
        
        #sin and cos
        th = norm(_bar)
        _hat = _bar / th
        cos_th = cos(th)
        sin_th = sin(th)
        th_t = dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        _1 = ((_1_bar, _1_t_bar,
               dot(_hat, _1_bar),
               cross(_hat, _1_bar)), (rec1,)
              for (_1_bar, _1_t_bar), (rec1,) in _1)
        
        #XXX there still might be a sign wrong here somewhere...
        rec2 = (_ for ((), (_,)) in _2)
        _2 = ((((cos_th * _1_bar -
                 sin_th * cross_th +
                 (1 - cos_th) * dot_th * _hat,
                 #
                 cos_th * _1_t_bar -
                 sin_th * cross(th_hat, _1_t_bar) +
                 (1 - cos_th) * dot(th_hat, _1_t_bar) * th_hat
                 +#
                 th_t * (sin_th * (dot_th * th_hat - _1_bar) -
                         cos_th * cross_th)
                 -#
                 sin_th * cross(_t_hat, _1_bar) +
                 (1 - cos_th) * (_hat * dot(_t_hat, _1_bar) +
                                 _t_hat * dot_th))
                if (rec1 and rec) ^ rec2.next()
                else (None, None)),
               (rec1 and rec,))
              for (_1_bar, _1_t_bar,
                   dot_th, cross_th), (rec1,) in _1)
        
        _, _1, _2 = yield None, None, _2

@PROCESS('vec.rot2nrt', NORMAL,
         Item('axis',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('inertial',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('rotating',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rot2nrt(_, _1, _2):
    """Rotating to inertial frame"""
    _, _1, _2 = yield
    while True:
        (_bar, _t_bar), (rec,) = _.next()
        
        #sin and cos
        th = norm(_bar)
        _hat = _bar / th
        cos_th = cos(th)
        sin_th = sin(th)
        th_t = dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        _2 = ((_2_bar, _2_t_bar,
               dot(_hat, _2_bar),
               cross(_hat, _2_bar)), (rec2,)
              for (_2_bar, _2_t_bar), (rec2,) in _2)
        
        #XXX there still might be a sign wrong here somewhere...
        rec1 = (_ for ((), (_,)) in _1)
        _1 = ((((cos_th * _2_bar +
                 sin_th * cross_th +
                 (1 - cos_th) * dot_th * _hat,
                 #
                 cos_th * _2_t_bar +
                 sin_th * cross(th_hat, _2_t_bar) +
                 (1 - cos_th) * dot(th_hat, _2_t_bar) * th_hat
                 +#
                 th_t * (sin_th * (dot_th * th_hat - _2_bar) +
                         cos_th * cross_th)
                 +#
                 sin_th * cross(_t_hat, _2_bar) +
                 (1 - cos_th) * (_hat * dot(_t_hat, _2_bar) +
                                 _t_hat * dot_th))
                if (rec2 and rec) ^ rec1.next()
                else (None, None)),
               (rec2 and rec,))
              for (_2_bar, _2_t_bar,
                   dot_th, cross_th), (rec2,) in _2)
        
        _, _1, _2 = yield None, _1, None

@PROCESS('vec.fun2obl', NORMAL,
         Item('node',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('fundamental',
              evs=('rec',), args=()
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('oblique',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def fun2obl(n, p, _1, _2):
    """Fundamental to oblique plane"""
    n, p, _1, _2 = yield
    while True:
        (n_bar, n_t_bar), (n_rec,) = n.next()
        (p_bar, p_t_bar), (p_rec,) = p.next()
        
        #vector triad
        t_bar = cross(p_bar, n_bar)
        t_t_bar = (cross(p_t_bar, n_bar) +
                   cross(p_bar, n_t_bar))
        
        #vector normal
        n = norm(n_bar)
        t = norm(t_bar)
        
        #unit vectors
        j_hat = t_bar / t
        i_hat = n_bar / n
        k_hat = cross(i_hat, j_hat)
        
        #vector normal rates
        n_t = dot(n_bar, n_t_bar) / _1
        t_t = dot(t_bar, t_t_bar) / _2
        
        #unit vector rates
        i_t_hat = (n * n_t_bar - n_t * n_bar) / n ** 2
        j_t_hat = (t * t_t_bar - t_t * t_bar) / t ** 2
        k_t_hat = (cross(i_t_hat, j_hat) +
                   cross(i_hat, j_t_hat))
        
        rec2 = (_ for ((), (_,)) in _2)
        _2 = ((((array([dot(_bar, i_hat),
                        dot(_bar, j_hat),
                        dot(_bar, k_hat)]),
                 array([dot(_1_t_bar, i_hat) + dot(_1_bar, i_t_hat),
                        dot(_1_t_bar, j_hat) + dot(_1_bar, j_t_hat),
                        dot(_1_t_bar, k_hat) + dot(_1_bar, k_t_hat)]))
                if (rec1 and n_rec and p_rec) ^ rec2.next()
                else (None, None)),
               (rec1 and rec,))
              for (_1_bar, _1_t_bar), (rec1,) in _1)
        
        n, p, _1, _2 = yield None, None, None, _2
    
@PROCESS('vec.obl2fun', NORMAL,
         Item('node',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('fundamental',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('oblique',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def obl2fun(n, p, _1, _2):
    """Oblique to fundamental plane"""
    n, p, _1, _2 = yield
    while True:
        (n_bar, n_t_bar), (n_rec,) = n.next()
        (p_bar, p_t_bar), (p_rec,) = p.next()
        
        #vector triad
        t_bar = cross(p_bar, n_bar)
        t_t_bar = (cross(p_t_bar, n_bar) +
                   cross(p_bar, n_t_bar))
        
        #vector lengths
        n = norm(n_bar)
        t = norm(t_bar)
        
        #unit vectors
        j_hat = t_bar / t
        i_hat = n_bar / n
        k_hat = cross(i_hat, j_hat)
        
        n_t = dot(n_bar, n_t_bar) / _1
        i_t_hat = (n * n_t_bar - n_t * n_bar) / n ** 2
        
        t_t = dot(t_bar, t_t_bar) / _2
        j_t_hat = (t * t_t_bar - t_t * t_bar) / t ** 2
        
        k_t_hat = (cross(i_t_hat, j_hat) +
                   cross(i_hat, j_t_hat))
        
        rec1 = (_ for ((), (_,)) in _1)
        _1 = ((((_2_bar[0] * i_hat + 
                 _2_bar[1] * j_hat +
                 _2_bar[2] * k_hat,
                 _2_t_bar[0] * i_hat + _2_bar[0] * i_t_hat +
                 _2_t_bar[1] * j_hat + _2_bar[1] * j_t_hat +
                 _2_t_bar[2] * k_hat + _bar[2] * k_t_hat)
                if (rec2 and n_rec and p_rec) ^ rec1.next()
                else (None, None)),
               (rec1 and rec,))
              for (_2_bar, _2_t_bar), (rec2,) in _2)
        
        n, p, _1, _2 = yield None, None, _1, None
    
@PROCESS('vec.rec2sph', NORMAL,
         Item('vector',
              evs=('rec',), args=(),
              ins=('rec', 'sph'), reqs=('_bar', '_t_bar'),
              outs=('sph',), pros=('r', 'r_t',
                                   'az', 'az_t',
                                   'el', 'el_t')))
def rec2sph(_):
    """Rectangular to spherical coordinates"""
    _, = yield
    while True:
        _ = (((r_bar, v_bar,
               norm(r_bar), atan2(r_bar[1],
                                  r_bar[0])), 
              __)
             for (r_bar, v_bar), __ in _)
        _ = (((r_bar, v_bar,
               r, dot(r_bar, v_bar) / r,
               az, asin(r_bar[2] / r),
               r ** 2 - r_bar[2] ** 2),
              __)
             for (r_bar, v_bar, r, az), __ in _)
        _ = (((r, r_t,
               atan2(r_bar[1], r_bar[0]),
               az, (r_bar[0] * v_bar[1] - 
                    r_bar[1] * v_bar[0]) / xy__2,
               el, (v_bar[2] - 
                    r_bar[2] * r_t / r) / xy__2), 
              __)
             for (_bar, _t_bar, r, r_t, az, el, xy__2), __ in _)
        _ = (((__ if rec ^ sph
               else (None,) * len(__)),
              (rec,))
             for __, (rec, sph) in _)
        _, = yield _,
    
@PROCESS('vec.sph2rec', NORMAL,
         Item('vector',
              evs=('sph',), args=(),
              ins=('sph', 'rec'), reqs=('r', 'r_t',
                                        'az', 'az_t',
                                        'el', 'el_t'),
              outs=('rec',), pros=('_bar', '_t_bar')))
def sph2rec(_):
    """Spherical to rectangular coordinates"""
    _, = yield
    while True:
        _ = (((r, r_t, az_t, el_t,
               cos(az), sin(az),
               cos(el), sin(el)),
              __)
             for (r, r_t, az, az_t, el, el_t), __ in _)
        _ = (((array([r * cos_az * cos_el,
                      r * sin_az * cos_el,
                      r * sin_el]),
               array([r_t * cos_az * cos_el -
                      r * (az_t * sin_az * cos_el +
                           el_t * cos_az * sin_el),
                      r_t * sin_az * cos_el +
                      r * (az_t * cos_az * cos_el -
                           el_t * sin_az * sin_el),
                      r_t * sin_el +
                      r * el_t * cos_el])),
              __)
             for (r, r_t, az_t, el_t,
                  cos_az, sin_az,
                  cos_el, sin_el), __ in _)
        _ = (((__ if sph ^ rec
               else (None,) * len(__)),
              (sph,))
             for __, (sph, rec) in _)
        _, = yield _,
