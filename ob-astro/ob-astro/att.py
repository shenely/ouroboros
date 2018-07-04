#built-in libraries
import math
import collections
import logging

#external libraries
import numpy
import scipy.linalg

#internal libraries
from ouroboros import REGISTRY, NORMAL, Item, PROCESS
from ouroboros.lib import libquat

#exports
__all__ = ('eulrot',
           'triad')

#constants
#...

base_rot = collections.namedtuple('rot', ('quat', 'bar'))
class rot(base_rot):
    """Rotation state vector"""

    def __new__(cls, quat, bar):
        assert isinstance(quat, libquat.quat)
        assert isinstance(bar, numpy.ndarray)
        assert bar.shape == (3,)
        assert numpy.issubdtype(bar.dtype, numbers.Real)
        return super(rot, cls).__new__(cls, quat, bar)

    def __add__(self, other):
        if isinstance(other, rot):
            return rot(self.quat * other.quat,
                       self.bar * other.bar)
        else:raise TypeError

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return rot(self.quat * other,
                       self.bar * other)
        else:raise TypeError

REGISTRY[rot] = ('$rot', lambda x:[x.quat, x.bar])
REGISTRY['$rot'] = lambda x:rot(*x)

@PROCESS('att.eulrot', NORMAL,
         Item('bod',
              evs=(), args=('eye',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('fun',
              evs=('i',), args=(),
              ins=(), reqs=('t', 'y'),
              outs=('o',), pros=('y_dot',)))
def eulrot(bod, fun):
    """Euler's rotation equations"""
    eye, = bod.next()
    inv_eye = scipy.linalg.inv(eye)

    right = yield
    while True:
        fun = right['fun']
        
        (t, y), _ = fun.next()
        (q, om) = y
        q_dot = libquat.mul(q, om / 2)
        om_dot = - numpy.dot(inv_eye,
                             numpy.cross(om,
                                         numpy.dot(eye, om)))
        y_dot = (q_dot, om_dot)
        fun = ((y_dot,), (False,))

        left = {'fun': fun}
        right = yield left

@PROCESS('att.triad', NORMAL,
         Item('src',
              evs=(), args=(),
              ins=(), reqs=('1_bar', '2_bar'),
              outs=(), pros=()),
         Item('trg',
              evs=(), args=(),
              ins=(), reqs=('1_bar', '2_bar'),
              outs=(), pros=()),
         Item('rot',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=(), pros=('_mat',)))
def triad():
    """Triad method"""
    
    right = yield
    while True:
        src, trg = (right['src'],
                    right['trg'])
        (r1_bar, r2_bar) = src.next()
        (R1_bar, R2_bar) = trg.next()
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
        
        rot = ((A_mat,), (True,))

        left = {'rot': rot}
        right = yield left
    
