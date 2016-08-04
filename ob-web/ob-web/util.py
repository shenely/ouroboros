import time

import simpy.core
import simpy.rt
import tornado.concurrent

from ..util import coroutine

__all__ = ["TornadoEnvironment"]
        
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
                    simpy.core.Environment.step(self)
                    future.set_result(True)
        routine = wrapper()
        routine.next()
        return future