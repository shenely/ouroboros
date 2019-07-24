#built-in libraries
import random

#external libraries
#...

#internal libraries
from ouroboros import Image, Node

#exports
__all__ = ("inc", "dec", "rand",
           "delta", "step")

#constants
#...


@Image(".func@inc",
       usr=Item(evs=(True,), args=("value",),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def inc(usr):
    """Increment"""
    value, = next(usr.data)

    yield
    while True:
        value += 1
        usr.data.send((value,))
        yield (usr.ctrl.send((True,)),)


@Image(".func@dec",
       usr=Item(evs=(True,), args=("value",),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def dec(usr):
    """Decrement"""
    value, = next(usr.data)

    yield
    while True:
        value -= 1
        usr.data.send((value,))
        yield (usr.ctrl.send((True,)),)


@Image(".func@rand",
       usr=Item(evs=(True,), args=(),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def rand(usr):
    """Random"""    
    yield
    while True:
        value = random.random()
        usr.data.send((value,))
        yield (usr.ctrl.send((True,)),)


@Image(".func@delta",
       fun=Item(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       usr=Item(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def delta(fun, usr):
    """Delta function"""
    t0, a = next(usr)
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        
        y_dot = a if (t == t0) else 0
        
        fun.data.send((y_dot,))
        yield (fun.ctrl.send((e in evs,)),)


@Image(".func@step",
       fun=Item(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       usr=Item(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def step(fun, usr):
    """Step function"""
    t0, a = next(usr)
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        
        y_dot = a if (t >= t0) else 0
        
        fun.data.send((y_dot,))
        yield (fun.ctrl.send((e in evs,)),)


@Image(".func@ramp",
       fun=Item(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       usr=Item(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def ramp(fun, usr):
    """Ramp function"""
    t0, a = next(usr)
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        
        y_dot = a * (t - t0) if (t >= t0) else 0
        
        fun.data.send((y_dot,))
        yield (fun.ctrl.send((e in evs,)),)