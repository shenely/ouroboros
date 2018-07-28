#built-in libraries
#...

#external libraries
import numpy.polynomial

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
#...

@PROCESS('mne.poly.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size','coeff'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Polynomial fit parser"""
    N, coeff = usr.next()
    P = numpy.polynomial.Polynomial(coeff)
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = P(raw / size)
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('mne.poly.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 'coeff'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Polynomial fit formatter"""
    N, coeff = usr.next()
    P = numpy.polynomial.Polynomial(coeff)
    size = float(2 ** N)
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int(next((root for root
                        in (P - eng).roots()
                        if root % 1 == 0
                        and root >= 0
                        and root < size), None))
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
