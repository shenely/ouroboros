import operator
import heapq
from threading import Thread

import simpy
import zmq
from zmq.eventloop.ioloop import IOLoop

from util import *

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
        self._zdata.connect("inproc://data")

        self._zctrl = context.socket(zmq.PAIR)
        self._zctrl.connect("inproc://ctrl")
        
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

    def __init__(self,args,ins,outs,reqs,pros):
        self._args = args
        
        self._reqs = reqs
        self._pros = pros
        
        self._ins = ins
        self._outs = outs
    
    def __call__(self,func):
        self._func = coroutine(func)
              
        def caller(sys,*pres):
            def wrapper():
                f = self._func(*sys.get([(pres[a[0]],a[1]) \
                                         for a in self._args]))

                sys.renew([(pres[o[0]],o[1]) for o in self._outs])

                while True:
                    yield sys.stop([(pres[i[0]],i[1]) for i in self._ins])

                    try:
                        try:
                            sys.set((lambda d: \
                                     {(pres[p[0]],p[1]): d[j] \
                                      for j,p in enumerate(self._pros)}) \
                                    (f.send(sys.get([(pres[r[0]],r[1]) \
                                                     for r in self._reqs]))))
                        except Go as err:
                            f = self._func(*sys.get([(pres[a[0]],a[1]) \
                                                     for a in self._args]))

                            raise err
                    except All:
                        outs = self._outs
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
                        outs = self._outs
                    finally:
                        sys.go([(pres[o[0]],o[1]) for o in outs])
                    
            sys.process(wrapper)
            
        return caller