#built-in libraries
import math

#external libraries
import numpy
import scipy.linalg

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
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('ref',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def abs2rel(src, trg, ref):
    """Absolute to relative origin"""
    right = yield
    while True:
        src, ref = (right['src'],
                    right['ref'])

        (_r_bar, _r_t_bar), _ = ref.next()
        trg = ((((_s_bar - _r_bar, _s_t_bar - _r_t_bar), (src_e,))
                if src_e else (None, None))
               for (_s_bar, _s_t_bar), (src_e,) in src)
        
        left = {'trg': trg}
        right = yield left
    
@PROCESS('vec.rel2abs', NORMAL,
         Item('src',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('trg',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('ref',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rel2abs(src, trg, ref):
    """Relative to absolute origin"""
    right = yield
    while True:
        trg, ref = (right['trg'],
                    right['ref'])

        (_r_bar, _r_t_bar), (ref_e,) = ref.next()
        src = ((((_t_bar + _r_bar, _t_t_bar + _r_t_bar), (trg_e,))
                if trg_e else (None, None))
               for (_t_bar, _t_t_bar), (trg_e,) in src)
        
        left = {'src': src}
        right = yield left
    
@PROCESS('vec.nrt2rot', NORMAL,
         Item('nrt',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('rot',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('ax',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def nrt2rot(nrt, rot, ax):
    """Inertial to rotating frame"""
    right = yield
    while True:
        nrt, ax = (right['nrt'],
                   right['ax'])
        (_bar, _t_bar), _ = ax.next()
        
        #sin and cos
        th = scipy.linalg.norm(_bar)
        _hat = _bar / th
        cos_th = math.cos(th)
        sin_th = math.sin(th)
        th_t = numpy.dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        nrt = (((i_bar, i_t_bar,
                 numpy.dot(_hat, i_bar),
                 numpy.cross(_hat, i_bar)), (rec_i,))
               for (i_bar, i_t_bar), (rec_i,) in nrt)
        
        #XXX there still might be a sign wrong here somewhere...
        rot = ((((cos_th * i_bar -
                  sin_th * cross_th +
                  (1 - cos_th) * dot_th * _hat,
                  #
                  cos_th * i_t_bar -
                  sin_th * numpy.cross(th_hat, i_t_bar) +
                  (1 - cos_th) * numpy.dot(th_hat, i_t_bar) * th_hat
                  +#
                  th_t * (sin_th * (dot_th * th_hat - i_bar) -
                          cos_th * cross_th)
                  -#
                  sin_th * numpy.cross(_t_hat, i_bar) +
                  (1 - cos_th) * (_hat * numpy.dot(_t_hat, i_bar) +
                                  _t_hat * dot_th)), (nrt_e,))
                if nrt_e else (None, None))
               for (i_bar, i_t_bar,
                    dot_th, cross_th), (nrt_e,) in nrt)

        left = {'rot': rot}
        right = yield left

@PROCESS('vec.rot2nrt', NORMAL,
         Item('nrt',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('rot',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('ax',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def rot2nrt(nrt, rot, ax):
    """Rotating to inertial frame"""
    right = yield
    while True:
        rot, ax = (right['rot'],
                   right['ax'])
        (_bar, _t_bar), _ = ax.next()
        
        #sin and cos
        th = scipy.linalg.norm(_bar)
        _hat = _bar / th
        cos_th = math.cos(th)
        sin_th = math.sin(th)
        th_t = numpy.dot(_bar, _t_bar) / th
        _t_hat = (th * _t_bar - th_t * _bar) / th ** 2
        
        #dot and cross products
        rot = (((r_bar, r_t_bar,
                 numpy.dot(_hat, r_bar),
                 numpy.cross(_hat, r_bar)), (rot_e,))
                for (r_bar, r_t_bar), (rot_e,) in rot)
        
        #XXX there still might be a sign wrong here somewhere...
        nrt = ((((cos_th * r_bar +
                  sin_th * cross_th +
                  (1 - cos_th) * dot_th * _hat,
                  #
                  cos_th * r_t_bar +
                  sin_th * cross(th_hat, r_t_bar) +
                  (1 - cos_th) * numpy.dot(th_hat, r_t_bar) * th_hat
                  +#
                  th_t * (sin_th * (dot_th * th_hat - r_bar) +
                          cos_th * cross_th)
                  +#
                  sin_th * numpy.cross(_t_hat, r_bar) +
                  (1 - cos_th) * (_hat * numpy.dot(_t_hat, r_bar) +
                                  _t_hat * dot_th)), (rot_e,))
                if rot_e else (None, None))
               for (r_bar, r_t_bar,
                    dot_th, cross_th), (rot_e,) in rot)

        left = {'nrt': nrt}
        right = yield left

@PROCESS('vec.fun2obl', NORMAL,
         Item('fun',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('obl',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('node',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def fun2obl(fun, obl, node, pole):
    """Fundamental to oblique plane"""
    right = yield
    while True:
        fun, node, pole = (right['fun'],
                           right['node'],
                           right['pole'])
        (n_bar, n_t_bar), _ = node.next()
        (p_bar, p_t_bar), _ = pole.next()
        
        #vector triad
        t_bar = numpy.cross(p_bar, n_bar)
        t_t_bar = (numpy.cross(p_t_bar, n_bar) +
                   numpy.cross(p_bar, n_t_bar))
        
        #vector normal
        n = scipy.linalg.norm(n_bar)
        t = scipy.linalg.norm(t_bar)
        
        #unit vectors
        j_hat = t_bar / t
        i_hat = n_bar / n
        k_hat = numpy.cross(i_hat, j_hat)
        
        #vector normal rates
        n_t = numpy.dot(n_bar, n_t_bar) / n
        t_t = numpy.dot(t_bar, t_t_bar) / t
        
        #unit vector rates
        i_t_hat = (n_t_bar - n_t * i_hat) / n
        j_t_hat = (t_t_bar - t_t * j_hat) / t
        k_t_hat = (numpy.cross(i_t_hat, j_hat) +
                   numpy.cross(i_hat, j_t_hat))
        
        obl = ((((numpy.array([numpy.dot(_bar, i_hat),
                               numpy.dot(_bar, j_hat),
                               numpy.dot(_bar, k_hat)]),
                  numpy.array([numpy.dot(f_t_bar, i_hat) +
                               numpy.dot(f_bar, i_t_hat),
                               numpy.dot(f_t_bar, j_hat) +
                               numpy.dot(f_bar, j_t_hat),
                               numpy.dot(f_t_bar, k_hat) +
                               numpy.dot(f_bar, k_t_hat)])), (fun_e,))
                if fun_e else (None, None))
               for (f_bar, f_t_bar), (fun_e,) in fun)

        left = {'obl': obl}
        right = yield left
    
@PROCESS('vec.obl2fun', NORMAL,
         Item('fun',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('rec',), pros=('_bar', '_t_bar')),
         Item('obl',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('node',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()),
         Item('pole',
              evs=(), args=(),
              ins=(), reqs=('_bar', '_t_bar'),
              outs=(), pros=()))
def obl2fun(fun, obl, node, pole):
    """Oblique to fundamental plane"""
    right = yield
    while True:
        obl, node, pole = (right['obl'],
                           right['node'],
                           right['pole'])
        (n_bar, n_t_bar), _ = node.next()
        (p_bar, p_t_bar), _ = pole.next()
        
        #vector triad
        t_bar = numpy.cross(p_bar, n_bar)
        t_t_bar = (numpy.cross(p_t_bar, n_bar) +
                   numpy.cross(p_bar, n_t_bar))
        
        #vector lengths
        n = scipy.linalg.norm(n_bar)
        t = scipy.linalg.norm(t_bar)
        
        #unit vectors
        j_hat = t_bar / t
        i_hat = n_bar / n
        k_hat = numpy.cross(i_hat, j_hat)
        
        n_t = numpy.dot(n_bar, n_t_bar) / n
        i_t_hat = (n * n_t_bar - n_t * n_bar) / n ** 2
        
        t_t = numpy.dot(t_bar, t_t_bar) / t
        j_t_hat = (t * t_t_bar - t_t * t_bar) / t ** 2
        
        k_t_hat = (numpy.cross(i_t_hat, j_hat) +
                   numpy.cross(i_hat, j_t_hat))
        
        fun = ((((o_bar[0] * i_hat + 
                  o_bar[1] * j_hat +
                  o_bar[2] * k_hat,
                  o_t_bar[0] * i_hat + o_bar[0] * i_t_hat +
                  o_t_bar[1] * j_hat + o_bar[1] * j_t_hat +
                  o_t_bar[2] * k_hat + o_bar[2] * k_t_hat), (obl_e,))
                if obl_e else (None, None))
               for (o_bar, o_t_bar), (obl_e,) in obl)

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
                 scipy.linalg.norm(r_bar),
                 math.atan2(r_bar[1], r_bar[0])), _)
               for (r_bar, v_bar), _ in vec)
        vec = (((r_bar, v_bar, r,
                 numpy.dot(r_bar, v_bar) / r,
                 az, math.asin(r_bar[2] / r),
                 r ** 2 - r_bar[2] ** 2), _)
               for (r_bar, v_bar, r, az), _ in vec)
        vec = (((r, r_t,
                 math.atan2(r_bar[1], r_bar[0]),
                 az, (r_bar[0] * v_bar[1] - 
                      r_bar[1] * v_bar[0]) / xy__2,
                 el, (v_bar[2] - 
                      r_bar[2] * r_t / r) / xy__2), 
                _)
               for (_bar, _t_bar, r, r_t, az, el, xy__2), _ in vec)
        vec = (((_, (rec,)) if rec ^ sph
                else (None, None))
               for _, (rec, sph) in vec)

        left = {'vec': vec}
        right = yield left
    
@PROCESS('vec.sph2rec', NORMAL,
         Item('vec',
              evs=('sph',), args=(),
              ins=('sph', 'rec'), reqs=('r', 'r_t',
                                        'az', 'az_t',
                                        'el', 'el_t'),
              outs=('rec',), pros=('_bar', '_t_bar')))
def sph2rec(vec):
    """Spherical to rectangular coordinates"""
    right = yield
    while True:
        vec = right['vec']
        
        vec = (((r, r_t, az_t, el_t,
                 math.cos(az), math.sin(az),
                 math.cos(el), math.sin(el)), _)
               for (r, r_t, az, az_t, el, el_t), _ in vec)
        vec = (((numpy.array([r * cos_az * cos_el,
                              r * sin_az * cos_el,
                              r * sin_el]),
                 numpy.array([r_t * cos_az * cos_el -
                              r * (az_t * sin_az * cos_el +
                                   el_t * cos_az * sin_el),
                              r_t * sin_az * cos_el +
                              r * (az_t * cos_az * cos_el -
                                   el_t * sin_az * sin_el),
                              r_t * sin_el +
                              r * el_t * cos_el])), _)
               for (r, r_t, az_t, el_t,
                    cos_az, sin_az,
                    cos_el, sin_el), _ in vec)
        vec = (((_, (sph,)) if sph ^ rec
                 else (None, None))
               for _, (sph, rec) in vec)

        left = {'vec': vec}
        right = yield left
