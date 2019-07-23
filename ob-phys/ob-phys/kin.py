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
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("y_dot",),
               outs=(True,), pros=("t", "y")))
def accum(fun, **kw):
    """Kinematic accumulator"""
    all(next(sub.data)
        for sub in kw.values())
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        (r, v) = y
        a = numpy.zeros_like(v)

        for sub in kw.values():
            sub.data.send((t, y))
            yield (sub.ctrl.send((e in evs,)),)
            y_dot, = next(sub.data)
            
            (r_dot, v_dot) = y_dot
            a += v_dot
        else:
            y_dot = libkin.kin(v, a)
            fun.data.send((y_dot,))
            yield (fun.ctrl.send((e in evs,)),)
            
