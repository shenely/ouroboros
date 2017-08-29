#built-in libraries
from math import cos, sin, asin, atan2

#external libraries
from numpy import ndarray, array, dot, cross
from scipy.linalg import norm

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__= ("abs2rel", "rel2abs",#relative
          "nrt2rot", "rot2nrt",#rotation
          "fun2obl", "obl2fun",#plane
          "rec2sph", "sph2rec")#coordinates

@PROCESS('vec.abs2rel', NORMAL,
         Item('src',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('trg',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('rel',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def abs2rel(src, trg, rel):
    """Absolute to relative origin"""
    right = yield
    while True:
        src, trg, rel = (right['src'],
                         right['trg'],
                         right['rel'])
        
        (_1_bar, _1_t_bar), (rec1,) = src.next()
        rec3 = (rec for (_, (rec,)) in _3)
        rel = ((((_2_bar - _1_bar, _2_t_bar - _1_t_bar)
                 if (rec1 and rec2) ^ rec3.next()
                 else (None, None)),
                (rec1 and rec2,))
               for (_2_bar, _2_t_bar), (rec2,) in trg)

        left = {'rel': rel}
        right = yield left
    
@PROCESS('vec.rel2abs', NORMAL,
         Item('src',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('trg',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('rel',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rel2abs(src, trg, rel):
    """Relative to absolute origin"""
    right = yield
    while True:
        src, trg, rel = (right['src'],
                         right['trg'],
                         right['rel'])
        
        (_1_bar, _1_t_bar), (rec1,) = src.next()
        rec2 = (rec for (_, (rec,)) in _2)
        trg = ((((_3_bar + _3_1_bar, _t_bar + _1_t_bar)
                 if (rec1 and rec3) ^ rec2.next()
                 else (None, None)),
                (rec1 and rec3,))
               for (_3_bar, _3_t_bar), (rec,) in rel)

        left = {'trg': trg}
        right = yield left
    
@PROCESS('vec.nrt2rot', NORMAL,
         Item('axis',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('nrt',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('rot',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def nrt2rot(axis, nrt, rot):
    """Inertial to rotating frame"""
    right = yield
    while True:
        axis, nrt, rot = (right['axis'],
                          right['nrt'],
                          right['rot'])
        (_bar, _t_bar), (rec,) = axis.next()
        
        #sin and cos
        th = norm(_bar)
        _hat = _bar / th
        cos_th = cos(th)
        sin_th = sin(th)
        th_t = dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        nrt = (((_1_bar, _1_t_bar,
                 dot(_hat, _1_bar),
                 cross(_hat, _1_bar)), (rec1,))
               for (_1_bar, _1_t_bar), (rec1,) in nrt)
        
        #XXX there still might be a sign wrong here somewhere...
        rec2 = (rec for (_, (rec,)) in rot)
        rot = ((((cos_th * _1_bar -
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
                    dot_th, cross_th), (rec1,) in nrt)

        left = {'rot': rot}
        right = yield left

@PROCESS('vec.rot2nrt', NORMAL,
         Item('axis',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('nrt',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('rot',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rot2nrt(axis, nrt, rot):
    """Rotating to inertial frame"""
    right = yield
    while True:
        axis, nrt, rot = (right['axis'],
                          right['nrt'],
                          right['rot'])
        (_bar, _t_bar), (rec,) = axis.next()
        
        #sin and cos
        th = norm(_bar)
        _hat = _bar / th
        cos_th = cos(th)
        sin_th = sin(th)
        th_t = dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        rot = (((_2_bar, _2_t_bar,
                 dot(_hat, _2_bar),
                 cross(_hat, _2_bar)), (rec2,))
                for (_2_bar, _2_t_bar), (rec2,) in rot)
        
        #XXX there still might be a sign wrong here somewhere...
        rec1 = (rec for (_, (rec,)) in nrt)
        nrt = ((((cos_th * _2_bar +
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
                    dot_th, cross_th), (rec2,) in rot)

        left = {'nrt': nrt}
        right = yield left

@PROCESS('vec.fun2obl', NORMAL,
         Item('node',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('fun',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('obl',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')))
def fun2obl(node, pole, fun, obl):
    """Fundamental to oblique plane"""
    right = yield
    while True:
        node, pole, fun, obl = (right['node'],
                                right['pole'],
                                right['fun'],
                                right['obl'])
        (n_bar, n_t_bar), (n_rec,) = node.next()
        (p_bar, p_t_bar), (p_rec,) = pole.next()
        
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
        n_t = dot(n_bar, n_t_bar) / n
        t_t = dot(t_bar, t_t_bar) / t
        
        #unit vector rates
        i_t_hat = (n_t_bar - n_t * i_hat) / n
        j_t_hat = (t_t_bar - t_t * j_hat) / t
        k_t_hat = (cross(i_t_hat, j_hat) +
                   cross(i_hat, j_t_hat))
        
        rec2 = (rec for (_, (rec,)) in obl)
        obl = ((((array([dot(_bar, i_hat),
                         dot(_bar, j_hat),
                         dot(_bar, k_hat)]),
                  array([dot(_1_t_bar, i_hat) + dot(_1_bar, i_t_hat),
                         dot(_1_t_bar, j_hat) + dot(_1_bar, j_t_hat),
                         dot(_1_t_bar, k_hat) + dot(_1_bar, k_t_hat)]))
                 if (rec1 and n_rec and p_rec) ^ rec2.next()
                 else (None, None)),
                (rec1 and rec,))
               for (_1_bar, _1_t_bar), (rec1,) in fun)

        left = {'obl': obl}
        right = yield left
    
@PROCESS('vec.obl2fun', NORMAL,
         Item('node',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('fun',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('obl',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def obl2fun(node, pole, fun, obl):
    """Oblique to fundamental plane"""
    right = yield
    while True:
        node, pole, fun, obl = (right['node'],
                                right['pole'],
                                right['fun'],
                                right['obl'])
        (n_bar, n_t_bar), (n_rec,) = node.next()
        (p_bar, p_t_bar), (p_rec,) = pole.next()
        
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
        
        n_t = dot(n_bar, n_t_bar) / n
        i_t_hat = (n * n_t_bar - n_t * n_bar) / n ** 2
        
        t_t = dot(t_bar, t_t_bar) / t
        j_t_hat = (t * t_t_bar - t_t * t_bar) / t ** 2
        
        k_t_hat = (cross(i_t_hat, j_hat) +
                   cross(i_hat, j_t_hat))
        
        rec1 = (rec for (_, (rec,)) in fun)
        fun = ((((_2_bar[0] * i_hat + 
                  _2_bar[1] * j_hat +
                  _2_bar[2] * k_hat,
                  _2_t_bar[0] * i_hat + _2_bar[0] * i_t_hat +
                  _2_t_bar[1] * j_hat + _2_bar[1] * j_t_hat +
                  _2_t_bar[2] * k_hat + _bar[2] * k_t_hat)
                 if (rec2 and n_rec and p_rec) ^ rec1.next()
                 else (None, None)),
                (rec1 and rec,))
               for (_2_bar, _2_t_bar), (rec2,) in obl)

        left = {'fun': fun}
        right = yield left
    
@PROCESS('vec.rec2sph', NORMAL,
         Item('vec',
              evs=('rec',), args=(),
              ins=('rec', 'sph'), reqs=('_bar', '_t_bar'),
              outs=('sph',), pros=('r', 'r_t',
                                   'az', 'az_t',
                                   'el', 'el_t')))
def rec2sph(vec):
    """Rectangular to spherical coordinates"""
    right = yield
    while True:
        vec = right['vec']
        
        vec = (((r_bar, v_bar,
                 norm(r_bar), atan2(r_bar[1],
                                    r_bar[0])), 
                _)
               for (r_bar, v_bar), _ in vec)
        vec = (((r_bar, v_bar,
                 r, dot(r_bar, v_bar) / r,
                 az, asin(r_bar[2] / r),
                 r ** 2 - r_bar[2] ** 2),
                _)
               for (r_bar, v_bar, r, az), _ in vec)
        vec = (((r, r_t,
                 atan2(r_bar[1], r_bar[0]),
                 az, (r_bar[0] * v_bar[1] - 
                      r_bar[1] * v_bar[0]) / xy__2,
                 el, (v_bar[2] - 
                      r_bar[2] * r_t / r) / xy__2), 
                _)
               for (_bar, _t_bar, r, r_t, az, el, xy__2), _ in vec)
        vec = (((_ if rec ^ sph
                 else (None,) * len(_)),
                (rec,))
               for _, (rec, sph) in vec)

        left = {'vec': vec}
        right = yield left
    
@PROCESS('vec.sph2rec', NORMAL,
         Item('vector',
              evs=('sph',), args=(),
              ins=('sph', 'rec'), reqs=('r', 'r_t',
                                        'az', 'az_t',
                                        'el', 'el_t'),
              outs=('rec',), pros=('_bar', '_t_bar')))
def sph2rec(_):
    """Spherical to rectangular coordinates"""
    right = yield
    while True:
        vec = right['vec']
        
        vec = (((r, r_t, az_t, el_t,
                 cos(az), sin(az),
                 cos(el), sin(el)),
                _)
               for (r, r_t, az, az_t, el, el_t), _ in vec)
        vec = (((array([r * cos_az * cos_el,
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
                _)
               for (r, r_t, az_t, el_t,
                    cos_az, sin_az,
                    cos_el, sin_el), _ in vec)
        vec = (((_ if sph ^ rec
                 else (None,) * len(_)),
                (sph,))
               for _, (sph, rec) in vec)

        left = {'vec': vec}
        right = yield left
