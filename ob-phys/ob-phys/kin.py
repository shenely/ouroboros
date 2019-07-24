# built-in libraries
# ...

# external libraries
import numpy

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.lib import libkin

# exports
__all__ = ("kin",
           "accum")

kin = Type(".phys#kin", "!phys/kin", libkin.kin,
           libkin.kin._asdict,
           lambda x: libkin.kin(**x))


@Image(".kin@accum",
       usr=Node(evs=(), args=("m",),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("F_bar",),
               outs=(True,), pros=("t", "r_bar", "v_bar")))
def accum(usr, fun, **kw):
    """Kinematic accumulator"""
    m, = next(usr)
    all(next(sub.data)
        for sub in kw.values())
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        (r_bar, v_bar) = y
        a_bar = numpy.zeros_like(v_bar)

        for sub in kw.values():
            sub.data.send((t, r_bar, v_bar))
            yield (sub.ctrl.send((e in evs,)),)
            F_bar, = next(sub.data)
            
            a_bar += F_bar / m
        else:
            y_dot = libkin.kin(v_bar, a_bar)
            fun.data.send((y_dot,))
            yield (fun.ctrl.send((e in evs,)),)
            
