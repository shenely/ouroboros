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
    poly, = next(usr.data)

    yield
    while True:
        x, = next(usr.data)
        y = poly(x)
        usr.data.send((y,))
        yield (usr.ctrl.send((True,)),)


@Image(".poly@roots",
       usr=Node(evs=(True,), args=("poly",),
                ins=(), reqs=(),
                outs=(False,), pros=("roots",)))
def roots(usr):
    """Roots of polynomial"""
    poly, = next(usr.data)

    yield
    roots = poly.roots
    usr.data.send((roots,))
    yield (usr.ctrl.send((True,)),)
