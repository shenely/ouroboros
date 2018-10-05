#built-in libraries
import datetime

#external libraries
import pytz

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('UNIX_TIME', 'REAL_TIME',
           'parse', 'format')

#constants
UNIX_TIME = datetime.datetime.fromtimestamp(0, tz=pytz.utc)
REAL_TIME = datetime.timedelta(microseconds=1000)

@PROCESS('data.date.parse', NORMAL,
         Item('usr',
              evs=(False,), args=('size', 't_dt', 'dt_td'),
              ins=(), reqs=('raw',),
              outs=(True,), pros=('eng',)))
def parse(usr):
    """Date/time object parser"""
    N, t_dt, dt_td = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (raw,), _ = usr.next()
        eng = t_dt + dt_td * raw
        usr = (((eng,), (True,)),)

        left = {'usr': usr}
        right = yield left

@PROCESS('data.date.format', NORMAL,
         Item('usr',
              evs=(True,), args=('size', 't_dt', 'dt_td'),
              ins=(), reqs=('eng',),
              outs=(False,), pros=('raw',)))
def format(usr):
    """Date/time object formatter"""
    N, t_dt, dt_td = usr.next()
    
    right = yield
    while True:
        usr = right['usr']

        (eng,), _ = usr.next()
        raw = int((eng - t_dt).total_seconds() /
                  dt_td.total_seconds())
        usr = (((raw,), (True,)),)

        left = {'usr': usr}
        right = yield left
