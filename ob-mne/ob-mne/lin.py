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

@PROCESS('mne.lin.parse', NORMAL,
         Item('usr',
              evs=('raw',), args=('size', 'lower', 'upper'),
              ins=(), reqs=('raw',),
              outs=('eng',), pros=('eng',)))
def parse(usr):
    """Linear relationship parser"""
    N, L, U = usr.next()
    
    base = L
    rate = U - L
    size = float((0b1 << N) - 1)
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = base + rate * (raw / size)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('mne.lin.format', NORMAL,
         Item('usr',
              evs=('eng',), args=('size', 'lower', 'upper'),
              ins=(), reqs=('eng',),
              outs=('raw',), pros=('raw',)))
def format(usr):
    """Linear relationship formatter"""
    N, L, U = usr.next()
    
    base = L
    rate = U - L
    size = float((0b1 << N) - 1)
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int(size * (eng - base) / rate)
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
