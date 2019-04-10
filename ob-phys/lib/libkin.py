# built-in libraries
import numbers
import collections

# external libraries
import numpy

# internal libraries
# ...

# exports
__all__ = ("kin",)

# constants
O_BAR = numpy.zeros((3,))


class kin(collections.namedtuple
           ("kin", ("r_bar", "v_bar"))):
    """Kinematic state vector"""

    def __new__(cls, r_bar=O_BAR, v_bar=O_BAR):
        assert isinstance(r_bar, numpy.ndarray)
        assert r_bar.shape == (3,)
        assert numpy.issubdtype(r_bar.dtype, numbers.Real)
        assert isinstance(v_bar, numpy.ndarray)
        assert v_bar.shape == (3,)
        assert numpy.issubdtype(v_bar.dtype, numbers.Real)
        return super(kin, cls).__new__(cls, r_bar, v_bar)

    def __add__(self, other):
        """Addition"""
        if isinstance(other, kin):
            return kin(self.r_bar * other.r_bar,
                       self.v_bar * other.v_bar)
        else:
            raise TypeError

    def __mul__(self, other):
        """Multiplication"""
        if isinstance(other, numbers.Real):
            return kin(self.r_bar * other,
                       self.v_bar * other)
        else:
            raise TypeError
