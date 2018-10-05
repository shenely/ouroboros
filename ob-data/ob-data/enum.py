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

@PROCESS('data.enum.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 'elems'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Enumerated values parser"""
    N, elems = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = elems.get(raw, None)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('data.enum.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'elems'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Enumerated values formatter"""
    N, elems, = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = elems.get(eng, None)
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
