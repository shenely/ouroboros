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
       usr=Node(evs=(), args=("m",),
                ins=(), reqs=(),
                outs=(), pros=()),
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar"),
                outs=(False,), pros=("F_bar",)),
       two=Node(evs=(), args=("m",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()))
def point(usr, one, two):
    """Point gravity"""
    m1, = next(usr.data)
    m2, = next(two.data)
    mu = GRAVITY_CONST * m1 * m2  # m3/kg/s2

    evs = yield
    while True:
        r1_bar, = next(one.data)
        r2_bar, = next(two.data)
        e, = next(fun.ctrl)
        
        r_bar = r1_bar - r2_bar
        F_bar = - mu * r_bar / scipy.linalg.norm(r_bar) ** 3
        
        fun.data.send((F_bar,))
        yield (fun.ctrl.send((e in evs,)),)
