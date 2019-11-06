# built-in libraries
import collections
import heapq

# external libraries
# ...

# internal libraries
from ouroboros import Image, Node

# exports
__all__= ("near", "lin")


##@Image(".interp@ode",
##       env=Node(evs=(True,), args=("t",),
##                ins=(True,), reqs=("t",),
##                outs=(), pros=()),
##       sys=Node(evs=(), args=(),
##                ins=(), reqs=("y",),
##                outs=(True,), pros=("y",)),
##       ode=Node(evs=(), args=(),
##                ins=(), reqs=(),
##                outs=(True,), pros=("t",)),
##       usr=Node(evs=(True, False), args=(),
##                ins=(True,), reqs=(),
##                outs=(True,), pros=()))


@Image(".interp@near",
       sys=Node(evs=(True,), args=("n",),
                ins=(True,), reqs=("x", "y"),
                outs=(), pros=("y",)),
       usr=Node(evs=(True,), args=(),
                ins=(True,), reqs=("x",),
                outs=(False,), pros=("y",)))
def near(sys, usr):
    """Nearest-neighbor interpolation"""
    q = collections.deque(maxlen=n)

    yield
    while True:
        e, = sys.ins()
        if e:
            x, y = sys.reqs
            q.append((x, y))

        e, = usr.ins()
        if e:
            x, = usr.reqs
            x, y = min(q, key=lambda a, b: abs(x - a))
            usr.pros = y,
            yield (usr.outs((True,)),)


@Image(".interp@lin",
       sys=Node(evs=(True,), args=("n",),
                ins=(True,), reqs=("x", "y"),
                outs=(), pros=("y",)),
       usr=Node(evs=(True,), args=(),
                ins=(True,), reqs=("x",),
                outs=(False,), pros=("y",)))
def lin(sys, usr):
    """Linear interpolation"""
    q = collections.deque(maxlen=n)

    yield
    while True:
        e, = sys.ins()
        if e:
            x, y = sys.reqs
            q.append((x, y))

        e, = usr.ins()()
        if e:
            x, = usr.reqs
            (x0, y0), (x1, y1) = (heapq.nsmallest
                                  (2, q, key=lambda a, b: abs(x - a)))
            t = (x - x0) / (x1 - x0)
            y = (1 - t) * y0 + t * y
            usr.pros = y,
            yield (usr.outs((True,)),)
