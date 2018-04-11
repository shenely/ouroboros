#built-in libraries
import functools
import datetime

#external libraries
import numpy.polynomial
import pytz

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('raw',
           'lin', 'pow', 'exp', 'log',
           'poly', 'enum', 'mask', 'date')

#constants
UNIX_TIME = datetime.fromtimestamp(0, tz=pytz.utc)
REAL_TIME = datetime.timedelta(microseconds=1000)

@PROCESS('tlm.raw', NORMAL,
         Item('tlm',
              evs=(False,), args=(),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def raw(tlm, eng):
    """Raw value"""
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = raw
        eng = (((raw,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.lin', NORMAL,
         Item('tlm',
              evs=(False,), args=('size',),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('lower', 'upper'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def lin(tlm, eng):
    """Linear relationship"""
    N, = tlm.next()
    L, U = eng.next()
    
    base = L
    rate = U - L
    size = float(2 ** N)
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = base + rate * (raw / size)
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.pow', NORMAL,
         Item('tlm',
              evs=(False,), args=('size',),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('lower', 'upper', 'exp'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def pow(tlm, eng):
    """Power law"""
    N, = tlm.next()
    L, U, k = eng.next()
    
    base = L
    rate = U - L
    size = float(2 ** N)
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = base + rate * (raw / size) ** k
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.exp', NORMAL,
         Item('tlm',
              evs=(False,), args=('size',),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('base', 'rate'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def exp(tlm, eng):
    """Exponential growth"""
    N, = tlm.next()
    base, rate = eng.next()
    size = float(2 ** N)
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        exp = rate * base ** (raw / size)
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.log', NORMAL,
         Item('tlm',
              evs=(False,), args=('size',),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('lower', 'upper'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def log(tlm, eng):
    """Logarithmic scale"""
    N, = tlm.next()
    L, U = eng.next()
    
    base = L
    rate = (U - L) / N
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        exp = base + rate * math.log(raw, 2)
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.poly', NORMAL,
         Item('tlm',
              evs=(False,), args=('size',),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('coeff'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def poly(tlm, eng):
    """Polynomial fit"""
    N, = tlm.next()
    coeff, = eng.next()
    P = numpy.polynomial.Polynomial(coeff)
    size = float(2 ** N)
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = P(raw / size)
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.enum', NORMAL,
         Item('tlm',
              evs=(False,), args=(),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('elems'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def enum(tlm, eng):
    """Enumerated values"""
    elems, = eng.next()
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = elems.get(raw, None)
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.mask', NORMAL,
         Item('tlm',
              evs=(False,), args=(),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('fields'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def mask(fields):
    """Masking bitfield"""
    fields, = eng.next()
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = [value for key, value
               in enumerate(fields)
               if raw & key]
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left

@PROCESS('tlm.date', NORMAL,
         Item('tlm',
              evs=(False,), args=(),
              ins=(), reqs=('raw',),
              outs=(), pros=()),
         Item('eng',
              evs=(), args=('t_dt', 'dt_td'),
              ins=(), reqs=(),
              outs=(True,), pros=('value',)))
def date():
    """Date/time object"""
    t_dt, dt_td = eng.next()
    
    right = yield
    while True:
        tlm = right['tlm']

        (raw,), _ = tlm.next()
        eng = t_dt + dt_td * raw
        eng = (((eng,), (True,)),)

        left = {'eng': eng}
        right = yield left
