#built-in libraries
import operator

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
#...

@PROCESS('mne.mask.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 'fields'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Masking bitfield"""
    N, fields = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = [value for key, value
               in enumerate(fields)
               if raw & key == key]
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('mne.mask.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'fields'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Masking bitfield formatter"""
    N, fields = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = reduce(operator.__or__,
                     (fields.get(value, 0)
                      for value in eng), 0)
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
