import datetime

from ..core import Process
from ..util import register

__all__= ["clock"]

KILO = 1e+3
MILLI = 1e-3

UNIX = datetime.datetime(1970, 1, 1)

@Process("clock.clock",
         (["t"], ["+1*"], {}, ["t"], []),
         (["t_dt", "dt_td"], [], {"clock":True}, [], ["t_dt"]))
def clock(t, t_dt, dt_td):
    """Clock"""
    t0 = t
    
    while True:
        t, = yield t_dt,
        
        t_dt += dt_td * (t - t0)
        
        t0 = t
        
        print t, t_dt
        
register(datetime.datetime, "$date",
         object_hook=(lambda value:
                      UNIX + datetime.timedelta(milliseconds=value)),
         default=(lambda obj:
                  int(KILO * (obj - UNIX).total_seconds())))
register(datetime.timedelta, "$elapse",
         object_hook=(lambda value:
                      datetime.timedelta(milliseconds=value)),
         default=(lambda obj:
                  int(KILO * obj.total_seconds())))