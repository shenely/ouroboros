#built-in libraries
# ...

#external libraries
import numpy

#internal libraries
from ouroboros import Type, Image, Node

#exports
__all__ = ("poly", "eval", "roots")

#constants
#...

# numpy.poly1d <-> JSON
poly = Type(".math#poly", "!math/poly", numpy.poly1d,
            lambda x: x.coeffs,
            numpy.poly1d)


@Image(".poly@eval",
       usr=Node(evs=(True,), args=("poly",),
                ins=(), reqs=("x",),
                outs=(False,), pros=("y",)))
def eval(usr):
    """Evaluate polynomial"""
    poly, = usr.data

    yield
    while True:
        x, = usr.reqs
        y = poly(x)
        usr.pros = y,
        yield (usr.outs((True,)),)


@Image(".poly@roots",
       usr=Node(evs=(True,), args=("poly",),
                ins=(), reqs=(),
                outs=(False,), pros=("roots",)))
def roots(usr):
    """Roots of polynomial"""
    poly, = usr.args

    yield
    roots = poly.roots
    usr.pros = roots,
    yield (usr.outs((True,)),)
