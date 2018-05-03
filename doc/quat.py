#built-in libraries
import math
import numbers

#external libraries
import numpy

#internal libraries
#...

#exports
__all__ = ('quat', 'unit',
           'pos', 'neg',
           'conj', 'norm', 'inv',
           'add', 'sub', 'mul', 'div',
           'rot')

#constants
O_BAR = numpy.zeros((3,))

def quat(p):
    """Quaternion"""
    if isinstance(p, tuple) and len(p) == 2:
        (p_one, p_bar) = p
        assert isinstance(p_one, numbers.Real)
        assert isinstance(p_bar, numpy.ndarray)
        assert p_bar.shape == (3,)
        assert p_bar.dtype == float
        return p
    else:
        (p_one, p_bar) = (0.0, O_BAR)
        if isinstance(p, numbers.Real):
            p_one = p
        elif isinstance(p, numpy.ndarray):
            assert p.shape == (3,)
            assert p.dtype == float
            p_bar = p
        else:
            raise TypeError
        return (p_one, p_bar)

def unit(p):
    """Unit quaternion (versor)"""
    (p_one, p_bar) = p
    _p_ = norm(p)
    return (p_one / _p_, p_bar / _p_)

def pos(p):
    """Positive"""
    (p_one, p_bar) = quat(p)
    return (p_one, p_bar)

def neg(p):
    """Negative"""
    (p_one, p_bar) = quat(p)
    return (- p_one, - p_bar)

def conj(p):
    """Conjugate"""
    (p_one, p_bar) = quat(p)
    return (p_one, - p_bar)

def norm(p):
    """Norm"""
    (p_one, p_bar) = quat(p)
    return math.sqrt(  p_one * p_one
                     + numpy.dot(p_bar, p_bar))

def inv(p):
    """Inverse (reciprocol)"""
    (p_one, p_bar) = quat(p)
    _p_ = p_one * p_one + numpy.dot(p_bar, p_bar)
    return (  p_one / _p_,
            - p_bar / _p_)

def add(p, q):
    """Addition"""
    (p_one, p_bar) = quat(p)
    (q_one, q_bar) = quat(q)
    return (p_one + q_one,
            p_bar + q_bar)

def sub(p, q):
    """Subtraction"""
    return add(p, sub(q))

def mul(p, q):
    """Multiplication"""
    (p_one, p_bar) = quat(p)
    (q_one, q_bar) = quat(q)
    return (  p_one * q_one
            - numpy.dot(p_bar, q_bar),
              p_one * q_bar
            + p_bar * q_one
            + numpy.cross(p_bar, q_bar))

def div(p, q):
    """Division"""
    return mul(p, inv(q))

def rot(p, q):
    """Rotation"""
    q = unit(q)
    return mul(q, mul(p, conj(q)))
