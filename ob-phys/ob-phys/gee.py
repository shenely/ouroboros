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
GRAVITY_CONST = 6.67808e-11  # m3/kg/s2


@Image(".phys@gee",
       usr=Node(evs=(), args=("m",),
                ins=(), reqs=(),
                outs=(), pros=()),
       nil=Node(evs=(), args=("m",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()),
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar",),
                outs=(False,), pros=("F_bar",)))
def point(usr, nil, one):
    """Point gravity"""
    m1, = next(usr.data)
    m0, = next(nil.data)
    mu = GRAVITY_CONST * m0 * m1  # m3/kg/s2

    evs = yield
    while True:
        r0_bar, = next(nil.data)
        r1_bar, = next(one.data)
        e, = next(one.ctrl)
        
        r_bar = r1_bar - r0_bar
        F_bar = - mu * r_bar / scipy.linalg.norm(r_bar) ** 3
        
        one.data.send((F_bar,))
        yield (one.ctrl.send((e in evs,)),)
