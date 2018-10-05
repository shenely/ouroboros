#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
#...

@PROCESS('data.pow.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 'lower', 'upper', 'exp'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Power law parser"""
    N, L, U, k = usr.next()
    
    base = L
    rate = U - L
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = base + rate * pow(raw / size, k)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('data.pow.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'lower', 'upper', 'exp'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Power law formatter"""
    N, L, U, k = usr.next()
    
    base = L
    rate = U - L
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int(size * pow((eng - base) / rate, 1.0 / k))
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
