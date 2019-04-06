# built-in libraries
import math
import collections
import logging

# external libraries
import numpy
import scipy.linalg

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.lib import libquat

# exports
__all__ = ("eulrot", "triad")

# constants
# ...


rot = Type(".att#rot", libquat.rot,
           lambda x: [x.quat, x.bar],
           libquat.rot)


@Image(".att@eulrot",
       bod=Node(evs=(), args=("eye",),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=("i",), args=(),
                ins=(), reqs=("t", "y"),
                outs=("o",), pros=("y_dot",)))
def eulrot(bod, fun):
    """Euler"s rotation equations"""
    eye, = bod.data.next()
    inv_eye = scipy.linalg.inv(eye)

    yield
    while True:
        t, y = fun.data.next()
        
        (q, om) = y
        q_dot = libquat.mul(q, om / 2)
        om_dot = - numpy.dot(
            inv_eye,
            numpy.cross(
                om, numpy.dot(eye, om)
            )
        )
        y_dot = rot(q_dot, om_dot)
        
        fun.data.send((y_dot,))
        yield (fun.ctrl.send((False,)),)


@Image(".att@triad",
       src=Node(evs=(), args=(),
                ins=(), reqs=("1_bar", "2_bar"),
                outs=(), pros=()),
       trg=Node(evs=(), args=(),
                ins=(), reqs=("1_bar", "2_bar"),
                outs=(), pros=()),
       rot=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(), pros=("_mat",)))
def triad(src, trg, rot):
    """Triad method"""
    yield
    while True:
        r1_bar, r2_bar = src.data.next()
        R1_bar, R2_bar = trg.data.next()
        
        r3_bar = numpy.cross(r1_bar, r2_bar)
        R3_bar = numpy.cross(R1_bar, R2_bar)

        s_hat = r1_bar / scipy.linalg.norm(r1_bar)
        S_hat = R1_bar / scipy.linalg.norm(R1_bar)
        m_hat = r3_bar / scipy.linalg.norm(r3_bar)
        M_hat = R3_bar / scipy.linalg.norm(R3_bar)
        s_cross_m = numpy.cross(s_bar, m_bar)
        S_cross_M = numpy.cross(S_bar, M_bar)

        r_mat = numpy.column_stack((s_bar, m_bar, s_cross_m))
        R_mat = numpy.column_stack((S_bar, M_bar, S_cross_M))
        A_mat = numpy.dot(R_mat, numpy.transpose(r_mat))
        
        rot.data.send((A_mat,))
        yield (rot.ctrl.send((True,)),)
    
