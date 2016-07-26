import time

import simpy.core
import tornado.ioloop
import tornado.concurrent

from core import System, Process
from util import coroutine
import clock, vec, geo, orb

class Caduceus(object):
    System = System
    Process = Process
    
    def __init__(self, env, loop):
        self._env = env
        self._loop = loop
        
        @coroutine
        def wrapper(future=None):
            while True:
                yield future
                future = self._env.step()
                self._loop.add_future(future, routine.send)
        routine = wrapper()
        
        self._future = tornado.concurrent.Future()
        self._future.add_done_callback(routine.send)
        
    def start(self, config):
        self._loop.add_callback(System, self._env, config)
        def wrapper():
            if not self._future.done():self._future.set_result(True)
        self._loop.add_callback(wrapper)
        
    def stop(self, name):
        self._loop.add_callback(System[name].halt)
        
class TornadoEnvironment(simpy.RealtimeEnvironment):
    
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