#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
BYTE = 8#bits

@PROCESS('data.raw.parse', NORMAL,
         Item('usr',
              evs=('raw',), args=(),
              ins=(), reqs=('raw',),
              outs=('eng',), pros=('eng',)))
def parse(usr):
    """Raw value parser"""
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = raw
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('data.raw.format', NORMAL,
         Item('usr',
              evs=('eng',), args=(),
              ins=(), reqs=('eng',),
              outs=('raw',), pros=('raw',)))
def format(usr):
    """Raw value formatter"""
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = eng
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
