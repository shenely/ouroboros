import types
import time
import json
import functools
import datetime

import numpy
import simpy.core
import simpy.rt
import tornado.concurrent

__all__ = ["coroutine",
           "Memoize",
           "TornadoEnvironment",
           "Go", "All", "Many", "One", "No",
           "dumps", "loads"]

KILO = 1e+3
MILLI = 1e-3

UNIX = datetime.datetime(1970, 1, 1)

#Unit vectors
O = numpy.array([0,0,0])
I = numpy.array([1,0,0])
J = numpy.array([0,1,0])
K = numpy.array([0,0,1])

def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper      

class Memoize(type):
    def __init__(self, *args, **kwargs):
        super(Memoize, self).__init__(*args, **kwargs)
        self._cache = {}
    
    def __len__(self):
        return len(self._cache)
    
    def __getitem__(self, key):
        return self._cache[key]
    
    def __setitem__(self, key, value):
        self._cache[key] = value
    
    def __delitem__(self, key):
        del self._cache[key]
        
    def __iter__(self):
        return iter(self._cache)
        
class TornadoEnvironment(simpy.rt.RealtimeEnvironment):
    
    def __init__(self, loop, *args, **kwargs):
        super(TornadoEnvironment, self).__init__(*args, **kwargs)
        self._loop = loop

    def step(self):
        """Process the next event after enough real-time has passed for the
        event to happen.

        The delay is scaled according to the real-time :attr:`factor`. With
        :attr:`strict` mode enabled, a :exc:`RuntimeError` will be raised, if
        the event is processed too slowly.

        """
        evt_time = self.peek()

        if evt_time is simpy.core.Infinity:
            raise simpy.core.EmptySchedule()

        real_time = self.real_start + (evt_time - self.env_start) * self.factor

        if self.strict and time.time() - real_time > self.factor:
            # Events scheduled for time *t* may take just up to *t+1*
            # for their computation, before an error is raised.
            raise RuntimeError('Simulation too slow for real time (%.3fs).' % (
                time.time() - real_time))

        future = tornado.concurrent.Future()
        @coroutine
        def wrapper():
            while True:
                yield
                delta = real_time - time.time()
                if delta > 0:
                    self._loop.call_later(delta, routine.next)
                else:
                    simpy.Environment.step(self)
                    future.set_result(True)
        routine = wrapper()
        routine.next()
        return future

class Go(Exception):pass

class All(Go):pass

class Many(Go):

    def __init__(self, *outs):
        self.value = outs

class One(Go):

    def __init__(self, out):
        self.value = out

class No(Go):pass

def object_hook(dct):
    if "$tuple" in dct:
        dct = tuple(dct["$tuple"])
    elif "$date" in dct:
        dct = UNIX + datetime.timedelta(milliseconds=dct["$date"])
    elif "$elapse" in dct:
        dct = datetime.timedelta(milliseconds=dct["$elapse"])
    elif "$array" in dct:
        dct = numpy.array(dct["$array"])

    return dct

def default(obj):
    if isinstance(obj, types.TupleType):
        obj = { "$tuple": list(obj) }
    elif isinstance(obj, datetime.datetime):
        obj = { "$date": int(KILO * (obj - UNIX).total_seconds()) }
    elif isinstance(obj, datetime.timedelta):
        obj = { "$elapse": int(KILO * obj.total_seconds()) }
    elif isinstance(obj, numpy.ndarray):
        obj = { "$array": obj.tolist() }
    else:
        raise#

    return obj

dumps = functools.partial(json.dumps, default=default)
loads = functools.partial(json.loads, object_hook=object_hook)