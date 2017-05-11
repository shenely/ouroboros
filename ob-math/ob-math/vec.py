from math import cos, sin, asin, atan2

from numpy import ndarray, array, dot, cross
from scipy.linalg import norm

from ..core import Process
from ..util import register

__all__= ["abs2rel", "rel2abs", 
          "nrt2rot", "rot2nrt", 
          "fun2obl", "obl2fun", 
          "rec2sph", "sph2rec"]

@Process('vec.abs2rel', lvl=1,
         Process.Item('source',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('target', 
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('relative',
                      ins=('rec',),
                      outs=('rec',),
                      pros=('_bar', '_t_bar')))
def abs2rel(*_):
    """Absolute to relative origin"""
    _1, _2, _3 = yield
    while True:
        (_1_bar, _1_t_bar), (rec1,) = _1.next()
        rec, = (_i for (_p, _i) in _3)
        _3 = (iter((_2_bar - _1_bar, _2_t_bar - _1_t_bar)
                   if (rec1 and rec2) ^ rec3.next()
                   else (None, None)),
              iter((rec1 and rec2,))
              for (_2_bar, _2_t_bar), (rec2,) in _2)
        _1, _2, _3 = yield (), (), _3
    
@Process('vec.rel2abs', lvl=1,
         Process.Item('source',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('target', 
                      ins=('rec',),
                      outs=('vec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('relative',
                      evs=('rec',),
                      ins=('rec',),
                      pros=('_bar', '_t_bar')))
def rel2abs(*_):
    """Relative to absolute origin"""
    _1, _2, _3 = yield
    while True:
        (_1_bar, _1_t_bar), (rec1,) = _1.next()
        rec2, = (_i for (_p, _i) in _2)
        _2 = (iter((_3_bar + _3_1_bar, _t_bar + _1_t_bar)
                   if (rec1 and rec3) ^ rec2.next()
                   else (None, None)),
              iter((rec1 and rec3,))
             for (_3_bar, _3_t_bar), (rec,) in _3)
        _1, _2, _3 = yield (), _2, ()
    
@Process('vec.nrt2rot', lvl=1,
         Process.Item('axis',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('inertial',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('rotating',
                      ins=('rec',),
                      outs=('rec',),
                      pros=('_bar', '_t_bar')))
def nrt2rot(*_):
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
        rec2, = (_i for (_p, _i) in _2)
        _2 = ((iter((cos_th * _1_bar -
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
               iter((rec1 and rec,)))
              for (_1_bar, _1_t_bar,
                   dot_th, cross_th), (rec1,) in _1)
        
        _, _1, _2 = yield (), (), _2

@Process('vec.rot2nrt', lvl=1,
         Process.Item('axis',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('inertial',
                      ins=('rec',),
                      outs=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('rotating',
                      evs=('rec',),
                      ins=('rec',),
                      pros=('_bar', '_t_bar')))
def rot2nrt(*_):
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
        rec1, = (_i for (_p, _i) in _1)
        _1 = ((iter((cos_th * _2_bar +
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
               iter((rec2 and rec,)))
              for (_2_bar, _2_t_bar,
                   dot_th, cross_th), (rec2,) in _2)
        
        _, _1, _2 = yield (), _1, ()

@Process('vec.fun2obl', lvl=1,
         Process.Item('node',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('pole',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('fundamental',
                      evs=('rec',),
                      ins=('rec',),
                      pros=('_bar', '_t_bar')),
         Process.Item('oblique',
                      ins=('rec',),
                      outs=('rec',),
                      pros=('_bar', '_t_bar')))
def fun2obl(*_):
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
        
        rec2, = (_i for (_p, _i) in _2)
        _2 = ((iter((array([dot(_bar, i_hat),
                            dot(_bar, j_hat),
                            dot(_bar, k_hat)]),
                     array([dot(_1_t_bar, i_hat) + dot(_1_bar, i_t_hat),
                            dot(_1_t_bar, j_hat) + dot(_1_bar, j_t_hat),
                            dot(_1_t_bar, k_hat) + dot(_1_bar, k_t_hat)]))
                    if (rec1 and n_rec and p_rec) ^ rec2.next()
                    else (None, None)),
               iter((rec1 and rec,)))
              for (_1_bar, _1_t_bar), (rec1,) in _1)
        
        n, p, _1, _2 = yield (), (), _1, ()
    
@Process('vec.obl2fun', lvl=1,
         Process.Item('node',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('pole',
                      evs=('rec',),
                      ins=('rec',),
                      reqs=('_bar', '_t_bar')),
         Process.Item('fundamental',
                      ins=('rec',),
                      outs=('rec',),
                      pros=('_bar', '_t_bar')),
         Process.Item('oblique',
                      evs=('rec',),
                      ins=('rec',),
                      pros=('_bar', '_t_bar')))
def obl2fun(*_):
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
        
        rec1, = (_i for (_p, _i) in _1)
        _1 = ((iter((_2_bar[0] * i_hat + 
                     _2_bar[1] * j_hat +
                     _2_bar[2] * k_hat,
                     _2_t_bar[0] * i_hat + _2_bar[0] * i_t_hat +
                     _2_t_bar[1] * j_hat + _2_bar[1] * j_t_hat +
                     _2_t_bar[2] * k_hat + _bar[2] * k_t_hat)
                    if (rec2 and n_rec and p_rec) ^ rec1.next()
                    else (None, None)),
               iter((rec1 and rec,)))
              for (_2_bar, _2_t_bar), (rec2,) in _2)
        
        n, p, _1, _2 = yield (), (), (), _2
    
@Process('vec.rec2sph', lvl=1,
         Process.Item('vector',
                      evs=('rec',),
                      ins=('rec', 'sph'),
                      reqs=('_bar', '_t_bar'),
                      outs=('sph',),
                      pros=('r', 'r_t',
                            'az', 'az_t',
                            'el', 'el_t')))
def rec2sph(*_):
    """Rectangular to spherical coordinates"""
    _, = yield
    while True:
        _, = yield _,
        
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
        _ = ((iter(__ if rec ^ sph
                   else (None,) * len(__)),
              iter((rec,)))
             for __, (rec, sph) in _)
    
@Process('vec.sph2rec', lvl=1,
         Process.Item('vector',
                      evs=('sph',),
                      ins=('sph', 'rec'),
                      reqs=('r', 'r_t',
                            'az', 'az_t',
                            'el', 'el_t'),
                      outs=('rec',),
                      pros=('_bar', '_t_bar')))
def sph2rec(*_):
    """Spherical to rectangular coordinates"""
    _, = yield
    while True:
        _, = yield _,
        
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
        _ = ((iter(__ if sph ^ rec
                   else (None,) * len(__)),
              iter((sph)))
             for __, (sph, rec) in _)
        
register(ndarray, "$array",
         object_hook=lambda value: array(value),
         default=lambda obj: obj.tolist())