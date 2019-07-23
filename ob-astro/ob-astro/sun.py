# built-in libraries
# ...

# external libraries
# ...

# internal libraries
from ouroboros import Image, Node
from ouroboros.lib import libsolar

# exports
__all__ = ("f10p7",)

# constants
#...


@Image("sun.f10p7",
       clk=Node(evs=(8601,), args=(),
                ins=(), reqs=("t_dt",),
                outs=(), pros=()),
       sun=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("f10p7",), pros=("f10p7",)))
def f10p7(clk, sun):
    """F10.7"""
    libsolar.getdata()
    yield
    while True:
        t_dt, = next(clk.data)
        f10p7 = libsolar.f10p7(t_dt)
        sun.data.send((f10p7,))
        yield (sun.ctrl.send((True,)),)
