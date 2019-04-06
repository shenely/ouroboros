# built-in libraries
import math
import itertools

# external libraries
import numpy
import scipy.linalg

# internal libraries
from ouroboros import Type, Image, Node

# exports
__all__= ("vector",
          "abs2rel", "rel2abs",  # absolute <-> relative frame
          "nrt2rot", "rot2nrt",  # inertial <-> rotating frame
          "fun2obl", "obl2fun",  # fundamental <-> oblique plane
          "rec2sph", "sph2rec")  # rectangular to spherical coordinates

# numpy.ndarray <-> JSON
vector = Type(".vec@vector", numpy.ndarray,
              numpy.ndarray.tolist,
              numpy.array)


@Image(".vec@abs2rel",
       src=Node(evs=(True,), args=(),
                ins=(True,), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       trg=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(True,), pros=("_bar", "_t_bar")),
       ref=Node(evs=(), args=(),
                ins=(), reqs=("_bar", "_t_bar"),
                outs=(), pros=()))
def abs2rel(src, trg, ref):
    """Absolute to relative origin"""
    yield
    while True:
        ref_bar, ref_t_bar = ref.data.next()
        src_bar, src_t_bar = src.data.next()
        
        trg_bar = src_bar - ref_bar
        trg_t_bar = src_t_bar - ref_t_bar

        trg.data.send((trg_bar, trg_t_bar))
        yield (trg.ctrl.send((True,)),)


@Image(".vec@rel2abs",
       src=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(True,), pros=("_bar", "_t_bar")),
       trg=Node(evs=(True,), args=(),
                ins=(True,), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       ref=Node(evs=(), args=(),
                ins=(), reqs=("_bar", "_t_bar"),
                outs=(), pros=()))
def rel2abs(src, trg, ref):
    """Relative to absolute origin"""
    yield
    while True:
        ref_bar, ref_t_bar = ref.data.next()
        trg_bar, trg_t_bar = trg.data.next()
        
        src_bar = trg_bar + ref_bar
        src_t_bar = trg_t_bar + ref_t_bar

        src.data.send((src_bar, src_t_bar))
        yield (src.ctrl.send((True,)),)

   
@Image(".vec@nrt2rot",
       nrt=Node(evs=(True,), args=(),
                ins=(True,), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       rot=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(True,), pros=("_bar", "_t_bar")),
       ax=Node(evs=(), args=(),
               ins=(), reqs=("_bar", "_t_bar"),
               outs=(), pros=()))
def nrt2rot(nrt, rot, ax):
    """Inertial to rotating frame"""
    yield
    while True:
        ax_bar, ax_t_bar = ax.data.next()
        nrt_bar, nrt_t_bar = nrt.data.next()
        
        #sin and cos
        th = scipy.linalg.norm(_bar)
        ax_hat = ax_bar / th
        cos_th = math.cos(th)
        sin_th = math.sin(th)
        th_t = numpy.dot(_bar, _t_bar) / th
        ax_t_hat = (th * ax_t_bar - th_t * ax_bar) / th ** 2
        
        #dot and cross products
        dot_th = numpy.dot(ax_hat, nrt_bar)
        cross_th = numpy.cross(ax_hat, nrt_bar)
        
        #XXX there still might be a sign wrong here somewhere...
        rot_bar = (cos_th * nrt_bar
                   - sin_th * cross_th
                   + (1 - cos_th) * dot_th * ax_hat)
        rot_t_bar = (cos_th * (nrt_t_bar - th_t * cross_th)
                     - sin_th * (numpy.cross(ax_t_hat, nrt_bar) +
                                 numpy.cross(ax_hat, nrt_t_bar) +
                                 th_t * (nrt_bar - dot_th * ax_hat))
                     + (1 - cos_th) * (ax_hat * (numpy.dot(ax_t_hat, nrt_bar) +
                                                 numpy.dot(ax_hat, nrt_t_bar)) +
                                       dot_th * ax_t_hat))

        rot.data.send((rot_bar, rot_t_bar))
        yield (rot.ctrl.send((True,)),)


@Image(".vec@rot2nrt",
       nrt=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(True,), pros=("_bar", "_t_bar")),
       rot=Node(evs=(True,), args=(),
                ins=(True,), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       ax=Node(evs=(), args=(),
               ins=(), reqs=("_bar", "_t_bar"),outs=(), pros=()))
def rot2nrt(nrt, rot, ax):
    """Rotating to inertial frame"""
    yield
    while True:
        ax_bar, ax_t_bar = ax.data.next()
        rot_bar, rot_t_bar = rot.data.next()
        
        #sin and cos
        th = scipy.linalg.norm(_bar)
        ax_hat = ax_bar / th
        cos_th = math.cos(th)
        sin_th = math.sin(th)
        th_t = numpy.dot(_bar, _t_bar) / th
        ax_t_hat = (th * ax_t_bar - th_t * ax_bar) / th ** 2
        
        #dot and cross products
        dot_th = numpy.dot(ax_hat, rot_bar)
        cross_th = numpy.cross(ax_hat, rot_bar)
        
        #XXX there still might be a sign wrong here somewhere...
        rot_bar = (cos_th * nrt_bar
                   + sin_th * cross_th
                   + (1 - cos_th) * dot_th * ax_hat)
        rot_t_bar = (cos_th * (nrt_t_bar + th_h * cross_th)
                     + sin_th * (numpy.cross(ax_t_hat, rot_bar) +
                                 numpy.cross(ax_hat, rot_t_bar) -
                                 th_t * (nrt_bar - dot_th * ax_hat))
                     + (1 - cos_th) * (ax_hat * (numpy.dot(ax_t_hat, rot_bar) +
                                                 numpy.dot(ax_hat, rot_t_bar)) +
                                       dot_th * ax_t_hat))

        rot.data.send((rot_bar, rot_t_bar))
        yield (rot.ctrl.send((True,)),)


@Image(".vec@fun2obl",
       fun=Node(evs=("rec",), args=(),
                ins=("rec",), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       obl=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("rec",), pros=("_bar", "_t_bar")),
       node=Node(evs=(), args=(),
                 ins=(), reqs=("_bar", "_t_bar"),
                 outs=(), pros=()),
       pole=Node(evs=(), args=(),
                 ins=(), reqs=("_bar", "_t_bar"),
                 outs=(), pros=()))
def fun2obl(fun, obl, node, pole):
    """Fundamental to oblique plane"""
    yield
    while True:
        n_bar, n_t_bar = node.data.next()
        p_bar, p_t_bar = pole.data.next()
        fun_bar, fun_t_bar = fun.data.next()
        
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

        obl_bar = numpy.array([numpy.dot(fun_bar, i_hat),
                               numpy.dot(fun_bar, j_hat),
                               numpy.dot(fun_bar, k_hat)])
        obl_t_bar = numpy.array([numpy.dot(fun_t_bar, i_hat) +
                                 numpy.dot(fun_bar, i_t_hat),
                                 numpy.dot(fun_t_bar, j_hat) +
                                 numpy.dot(fun_bar, j_t_hat),
                                 numpy.dot(fun_t_bar, k_hat) +
                                 numpy.dot(fun_bar, k_t_hat)])

        obl.data.send((obl_bar, obl_t_bar))
        yield (obl.ctrl.send((True,)),)

    
@Image(".vec@obl2fun",
       fun=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("rec",), pros=("_bar", "_t_bar")),
       obl=Node(evs=("rec",), args=(),
                ins=("rec",), reqs=("_bar", "_t_bar"),
                outs=(), pros=()),
       node=Node(evs=(), args=(),
                 ins=(), reqs=("_bar", "_t_bar"),
                 outs=(), pros=()),
       pole=Node(evs=(), args=(),
                 ins=(), reqs=("_bar", "_t_bar"),
                 outs=(), pros=()))
def obl2fun(fun, obl, node, pole):
    """Oblique to fundamental plane"""
    yield
    while True:
        n_bar, n_t_bar = node.next()
        p_bar, p_t_bar = pole.next()
        obl_bar, obl_t_bar = obl.data.next()
        
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
        i_t_hat = (n * n_t_bar - n_t * n_bar) / (n * n)
        j_t_hat = (t * t_t_bar - t_t * t_bar) / (t * t)
        k_t_hat = (numpy.cross(i_t_hat, j_hat) +
                   numpy.cross(i_hat, j_t_hat))

        fun_bar = (obl_bar[0] * i_hat +
                   obl_bar[1] * j_hat +
                   obl_bar[2] * k_hat)
        fun_t_bar = (obl_t_bar[0] * i_hat + obl_bar[0] * i_t_hat +
                     obl_t_bar[1] * j_hat + obl_bar[1] * j_t_hat +
                     obl_t_bar[2] * k_hat + obl_bar[2] * k_t_hat)

        fun.data.send((fun_bar, fun_t_bar))
        yield (fun.ctrl.send((True,)),)

    
@Image(".vec@rec2sph",
       vec=Node(evs=("rec",), args=(),
                ins=(), reqs=("_bar"),
                outs=("sph",), pros=("r", "az", "el")))
def rec2sph(vec):
    """Rectangular to spherical coordinates"""
    yield
    while True:
        _bar, = vec.data.next()
        
        r = scipy.linalg.norm(_bar)
        az = math.atan2(_bar[1], _bar[0])
        el = math.asin(_bar[2] / r)

        vec.data.send((r, az, el))
        yield (vec.ctrl.send((True,)),)

    
@Image(".vec@sph2rec",
       vec=Node(evs=("sph",), args=(),
                ins=(), reqs=("r", "az", "el"),
                outs=("rec",), pros=("_bar")))
def sph2rec(vec):
    """Spherical to rectangular coordinates"""
    yield
    while True:
        r, az, el = vec.data.next()
        
        cos_az = math.cos(az)
        sin_az = math.sin(az)
        cos_el = math.cos(el)
        sin_el = math.sin(el)
        
        _bar = numpy.array([r * cos_az * cos_el,
                            r * sin_az * cos_el,
                            r * sin_el])

        vec.data.send((_bar,))
        yield (vec.ctrl.send((True,)),)
