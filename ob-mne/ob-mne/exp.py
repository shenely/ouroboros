#built-in libraries
import math

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
#...

@PROCESS('mne.exp.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 'base', 'rate'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Exponential growth parser"""
    N, base, rate = usr.next()
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = rate * base ** (raw / size)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('mne.exp.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'base', 'rate'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Exponential growth formatter"""
    N, base, rate = usr.next()
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int(size * math.log(eng / rate, base))
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
