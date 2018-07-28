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

@PROCESS('mne.log.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 'lower', 'upper'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Logarithmic scale parser"""
    N, L, U = usr.next()
    
    base = L
    rate = (U - L) / N
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = base + rate * math.log(raw, 2)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('mne.log.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'lower', 'upper'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Logarithmic scale formatter"""
    N, L, U = usr.next()
    
    base = L
    rate = (U - L) / N
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int(2 ** ((eng - base) / rate))
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
