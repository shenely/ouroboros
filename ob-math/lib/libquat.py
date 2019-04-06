# built-in libraries
import math
import numbers
import collections

# external libraries
import numpy

# internal libraries
# ...

# exports
__all__ = ("quat", "rot")

# constants
O_BAR = numpy.zeros((3,))


class quat(collections.namedtuple
           ("quat", ("one", "bar"))):
    """Quaternion"""

    def __new__(cls, one=0.0, bar=O_BAR):
        assert isinstance(one, numbers.Real)
        assert isinstance(bar, numpy.ndarray)
        assert bar.shape == (3,)
        assert numpy.issubdtype(bar.dtype, numbers.Real)
        return super(quat, cls).__new__(cls, one, bar)

    @classmethod
    def _init_(cls, p):
        if isinstance(p, quat):return p
        elif isinstance(p, tuple) and len(p) == 2:
            p_one, p_bar = p
            return super(quat, cls).__new__(cls, p_one, p_bar)
        elif isinstance(p, numbers.Real):
            return super(quat, cls).__new__(cls, one=p)
        elif isinstance(p, numpy.ndarray):
            return super(quat, cls).__new__(cls, bar=p)
        else:
            raise ValueError

    def _unit_(self):
        """Unit quaternion (versor)"""
        (p_one, p_bar) = self
        _p_ = self._norm_()
        return quat(p_one / _p_, p_bar / _p_)

    def __pos__(self):
        """Positive"""
        (p_one, p_bar) = self
        return quat(p_one, p_bar)

    def __neg__(self):
        """Negative"""
        (p_one, p_bar) = self
        return quat(- p_one, - p_bar)

    def _conj_(self):
        """Conjugate"""
        (p_one, p_bar) = self
        return quat(p_one, - p_bar)

    def __abs__(self):
        """Norm"""
        (p_one, p_bar) = self
        return math.sqrt(p_one * p_one +
                         numpy.dot(p_bar, p_bar))

    def __invert__(self):
        """Inverse (reciprocol)"""
        (p_one, p_bar) = self
        _p_ = p_one * p_one + numpy.dot(p_bar, p_bar)
        return quat(+ p_one / _p_,
                    - p_bar / _p_)

    def __add__(self, other):
        """Addition"""
        (p_one, p_bar) = self
        (q_one, q_bar) = quat._init_(other)
        return quat(p_one + q_one,
                    p_bar + q_bar)

    def __sub__(self, other):
        """Subtraction"""
        return self + -quat._init_(other)

    def __mul__(self, other):
        """Multiplication"""
        (p_one, p_bar) = self
        (q_one, q_bar) = quat._init_(other)
        return quat(p_one * q_one - numpy.dot(p_bar, q_bar),
                    p_one * q_bar + p_bar * q_one + numpy.cross(p_bar, q_bar))

    def __div__(self, other):
        """Division"""
        return self * ~quat._init_(other)

    def _rot_(self, other, inv=False):
        """Rotation"""
        other = quat._init_(other)
        return ((other * (self * other._conj_()))
                if not inv else
                (other._conj_() * (self * other)))


class rot(collections.namedtuple
          ("rot", ("quat", "bar"))):
    """Rotation state vector"""

    def __new__(cls, quat, bar):
        assert isinstance(quat, libquat.quat)
        assert isinstance(bar, numpy.ndarray)
        assert bar.shape == (3,)
        assert numpy.issubdtype(bar.dtype, numbers.Real)
        return super(rot, cls).__new__(cls, quat, bar)

    def __add__(self, other):
        """Addition"""
        if isinstance(other, rot):
            return rot(self.quat * other.quat,
                       self.bar * other.bar)
        else:
            raise TypeError

    def __mul__(self, other):
        """Multiplication"""
        if isinstance(other, numbers.Real):
            return rot(self.quat * other,
                       self.bar * other)
        else:
            raise TypeError
