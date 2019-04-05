###built-in libraries
##import math
##import random
##
###external libraries
###...
##
###internal libraries
##from ouroboros import NORMAL, Item, PROCESS
##
###exports
##__all__ = (
##    'inc', 'dec', 'rand'
##)
##
###constants
###...
##
##@PROCESS('fun.inc', NORMAL,
##         Item('usr',
##              evs=('inc',), args=(),
##              ins=(), reqs=('x',),
##              outs=(), pros=('x',)))
##def inc(usr):
##    """Increment"""    
##    right = yield
##    while True:
##        usr = right['usr']
##        (value,), _ = usr.next()
##        value += 1
##        usr = (((value,), ()),)
##        left = {'usr': usr}
##        right = yield left
##
##@PROCESS('fun.dec', NORMAL,
##         Item('usr',
##              evs=('dec',), args=(),
##              ins=(), reqs=('x',),
##              outs=(), pros=('x',)))
##def dec(usr):
##    """Decrement"""    
##    right = yield
##    while True:
##        usr = right['usr']
##        (value,), _ = usr.next()
##        value += 1
##        usr = (((value,), ()),)
##        left = {'usr': usr}
##        right = yield left
##
##@PROCESS('fun.rand', NORMAL,
##         Item('usr',
##              evs=('rand',), args=(),
##              ins=(), reqs=(),
##              outs=(), pros=('x',)))
##def rand(usr):
##    """Random"""    
##    yield
##    while True:
##        value = random.random()
##        usr = (((value,), ()),)
##        left = {'usr': usr}
##        yield left
