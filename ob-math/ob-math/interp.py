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
        e, = next(sys.ctrl)
        if e:
            x, y = next(sys.data)
            q.append((x, y))

        e, = next(usr.ctrl)
        if e:
            x, = next(usr.data)
            x, y = min(q, key=lambda a, b: abs(x - a))
            usr.data.send((y,))
            yield (usr.ctrl.send((True,)),)


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
        e, = next(sys.ctrl)
        if e:
            x, y = next(sys.data)
            q.append((x, y))

        e, = next(usr.ctrl)
        if e:
            x, = next(usr.data)
            (x0, y0), (x1, y1) = (heapq.nsmallest
                                  (2, q, key=lambda a, b: abs(x - a)))
            t = (x - x0) / (x1 - x0)
            y = (1 - t) * y0 + t * y
            usr.data.send((y,))
            yield (usr.ctrl.send((True,)),)
