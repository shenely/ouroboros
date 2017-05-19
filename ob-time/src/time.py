import datetime

from ..core import Process
from ..util import One, register

__all__= ["epoch", "clock", "at", "after", "every"]

KILO = 1e+3
MILLI = 1e-3

UNIX = datetime.datetime(1970, 1, 1)

@Process("time.epoch",
         ([], ["@0"], {}, ["t"], []),
         (["t_dt"], [], {"tick":True}, [], ["t_dt"]))
def epoch(t_dt):
    """Epoch"""
    t, = yield
    print t, t_dt
    yield t_dt,

@Process("time.clock",
         (["t"], ["+1*"], {}, ["t"], []),
         (["t_dt", "dt_td"], [], {"tick":True}, [], ["t_dt"]))
def clock(t, t_dt, dt_td):
    """Clock"""
    t0 = t
    
    while True:
        t, = yield t_dt,
        t_dt += dt_td * (t - t0)
        t0 = t
        print t, t_dt

@Process("time.at",
         (["t_dt"], ["tick"], {}, ["t_dt"], []),
         (["t_dt"], [], {"tock":False}, [], []))
def at(t_dt, t1_dt):
    """At"""
    
    if t_dt <= t1_dt:
        t, = yield
        while t_dt < t1_dt:
            t_dt, = yield
        else:
            raise One("tock")

@Process("time.after",
         (["t_dt"], ["tick"], {}, ["t_dt"], []),
         (["dt_td"], [], {"tock":False}, [], []))
def after(t_dt, dt_td):
    """After"""
    t0_dt = t_dt
    t1_dt = t0_dt + dt_td
    
    if t_dt <= t1_dt:
        t, = yield
        while t_dt < t1_dt:
            t_dt, = yield
        else:
            raise One("tock")

@Process("time.every",
         (["t_dt"], ["tick"], {}, ["t_dt"], []),
         (["dt_td"], [], {"tock":False}, [], []))
def every(t_dt, dt_td):
    """Every"""
    t0_dt = t_dt
    t1_dt = t0_dt + dt_td
    
    t, = yield
    while t_dt < t1_dt:
        t_dt, = yield
    else:
        raise One("tock")
        
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