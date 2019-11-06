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
       usr=Node(evs=(True,), args=("value",),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def inc(usr):
    """Increment"""
    value, = usr.args

    yield
    while True:
        value += 1
        usr.pros = value,
        yield (usr.outs((True,)),)


@Image(".func@dec",
       usr=Node(evs=(True,), args=("value",),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def dec(usr):
    """Decrement"""
    value, = usr.args

    yield
    while True:
        value -= 1
        usr.pros = value,
        yield (usr.outs((True,)),)


@Image(".func@rand",
       usr=Node(evs=(True,), args=(),
                ins=(), reqs=(),
                outs=(False,), pros=("value",)))
def rand(usr):
    """Random"""
    yield
    while True:
        value = random.random()
        usr.pros = value,
        yield (usr.outs((True,)),)


@Image(".func@delta",
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("f",)),
       usr=Node(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def delta(fun, usr):
    """Delta function"""
    t0, a = usr.args
    
    evs = yield
    while True:
        t, y = fun.reqs
        e, = fun.ins()
        
        f = a if (t == t0) else 0
        
        fun.pros = f,
        yield (fun.outs((e in evs,)),)


@Image(".func@step",
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("f",)),
       usr=Node(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def step(fun, usr):
    """Step function"""
    t0, a = usr.args
    
    evs = yield
    while True:
        t, y = fun.reqs
        e, = fun.ins()
        
        f = a if (t >= t0) else 0
        
        fun.pros = f,
        yield (fun.outs((e in evs,)),)


@Image(".func@ramp",
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("f",)),
       usr=Node(evs=(True,), args=("t", "a"),
                ins=(), reqs=(),
                outs=(), pros=()))
def ramp(fun, usr):
    """Ramp function"""
    t0, a = usr.data
    
    evs = yield
    while True:
        t, y = fun.reqs
        e, = fun.ins()
        
        f = a * (t - t0) if (t >= t0) else 0
        
        fun.pros = f,
        yield (fun.outs((e in evs,)),)
