import operator
import heapq
from threading import Thread
from collections import namedtuple

import simpy
import zmq
from zmq.eventloop.ioloop import IOLoop

from util import *

__all__ = ["Config", "System", "Process"]

Config = namedtuple("Config", ["args", "ins", "outs", "reqs", "pros"])

class System(object):

    def __init__(self,t=0,**kwargs):
        self._env = simpy.RealtimeEnvironment()
        
        kwargs["t"] = t

        self._data = {(None,kw):kwargs[kw] for kw in kwargs}
        self._ctrl = dict()
        
        self._clock = [self._data[(None,"t")]]
        self.clock()

        context = zmq.Context.instance()

        self._zdata = context.socket(zmq.PAIR)
        self._zdata.connect("inproc://zdata")

        self._zctrl = context.socket(zmq.PAIR)
        self._zctrl.connect("inproc://zctrl")
        
    def init(self,prefix,**kwargs):
        self.set({(prefix,kw):kwargs[kw] for kw in kwargs})

    def run(self):
        IOLoop.instance().add_callback(Thread(target=self._env.run).start)
        IOLoop.instance().start()

    def clock(self):
        def wrapper():
            while True:
                yield self._env.timeout(1)
                
                self._data[(None,"t")] = heapq.heappop(self._clock)
                
        self._env.process(wrapper())
        
    def at(self,t):
        name = "@{0:d}".format(t)
        
        if name not in self._ctrl:
            def wrapper():
                heapq.heappush(self._clock,t)
                
                self._ctrl[(None,name)] = self._env.event()
                
                while self._data["t"] > t:
                    yield self._env.timeout(1)
                else:
                    self._ctrl[(None,name)].succeed()
                
        self._env.process(wrapper())
        
        return name
        
    def after(self,dt):
        name = "+{0:d}".format(dt)
        
        if name not in self._ctrl:
            def wrapper():
                t = self._data[(None,"t")] + dt
                heapq.heappush(self._clock,t)
                
                self._ctrl[(None,name)] = self._env.event()
            
                while self._data[(None,"t")] != t:
                    yield self._env.timeout(1)
                else:
                    self._ctrl[(None,name)].succeed()
                    
            self._env.process(wrapper())
        
        return name
        
    def every(self,dt,until=None):
        name = "+{0:d}*".format(dt)
        
        if name not in self._ctrl:
            def wrapper():
                t = self._data[(None,"t")] + dt
                heapq.heappush(self._clock,t)
                
                self._ctrl[(None,name)] = self._env.event()
            
                while until is None or t < until:
                    if self._data[(None,"t")] == t:
                        t = self._data[(None,"t")] + dt
                        heapq.heappush(self._clock,t)
                        
                        self._ctrl[(None,name)].succeed()
                        self._ctrl[(None,name)] = self._env.event()
                        
                    yield self._env.timeout(1)
                    
            self._env.process(wrapper())
        
        return name

    def get(self,keys):
        return [self._data[k] for k in keys]

    def set(self,keys):
        self._data.update(keys)
        self._zdata.send(dumps([{"key":k,"value":keys[k]} \
                                for k in keys]))

    def renew(self,keys):
        self._ctrl.update({k: self._env.event() for k in keys})

    def stop(self,keys):
        return reduce(operator.__or__,[self._ctrl[k] for k in keys])

    def go(self,keys):
        map(simpy.Event.succeed,[self._ctrl[k] for k in keys])
        self._zctrl.send(dumps(keys))

        self.renew(keys)

    def process(self,func):
        self._env.process(func())

class Process(object):

    def __init__(self,*conf):
        self._conf = [Config(*c) for c in conf]
    
    def __call__(self,func):
        self._func = coroutine(func)
              
        def caller(sys,*pres):
            def wrapper():
                f = self._func(*sys.get([(pres[j],a) \
                                         for j,c in enumerate(self._conf) \
                                         for a in c.args]))

                sys.renew([(pres[j],o) \
                           for j,c in enumerate(self._conf) \
                           for o in c.outs])

                while True:
                    yield sys.stop([(pres[j],i) \
                                    for j,c in enumerate(self._conf) \
                                    for i in c.ins])

                    try:
                        try:
                            sys.set((lambda d: \
                                     {(pres[j],p): d[k] \
                                      for k,(j,p) in enumerate([(j,p) \
                                                                for j,c in enumerate(self._conf) \
                                                                for p in c.pros])}) \
                                    (f.send(sys.get([(pres[j],r) \
                                                     for j,c in enumerate(self._conf) \
                                                     for r in c.reqs]))))
                        except Go as err:
                            f = self._func(*sys.get([(pres[j],a) \
                                                     for j,c in enumerate(self._conf) \
                                                     for a in c.args]))

                            raise err
                    except All:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs]
                    except Many as err:
                        outs = err.value
                    except One as err:
                        outs = [err.value]
                    except No:
                        outs = []
                    except:
                        outs = []
                        raise
                    else:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs]
                    finally:
                        sys.go([(pres[j],o) for j,o in outs])
                    
            sys.process(wrapper)
            
        return caller