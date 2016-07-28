import time

import simpy.core
import tornado.ioloop
import tornado.concurrent

from .core import System, Process
from .util import coroutine
from . import clock, vec, geo, orb

class Ouroboros(object):
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