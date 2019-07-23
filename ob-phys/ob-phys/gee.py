# built-in libraries
# ...

# external libraries
import scipy.linalg

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.lib import libkin

# exports
__all__ = ("point",)

# constants
GRAVITY_CONST = 6.67808e-20  # km3/kg/s2


@Image(".phys@gee",
       one=Node(evs=(), args=("m",),
                ins=(), reqs=(),
                outs=(), pros=()),
       two=Node(evs=(), args=("m",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)))
def point(one, two, fun):
    """Point gravity"""
    m1, = next(one.data)
    m2, = next(two.data)
    mu = GRAVITY_CONST * m1 * m2  # m3/kg/s2

    evs = yield
    while True:
        r2, = next(two.data)
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        
        (r1, v1) = y
        r = r1 - r2
        r1_dot = v1
        v1_dot = - mu *r / scipy.linalg.norm(r) ** 3
        y_dot = libkin.kin(r1_dot, v1_dot)
        
        fun.data.send((y_dot,))
        yield (fun.ctrl.send((e in evs,)),)
