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
    """Simulation system"""

    def __init__(self, t=0, **kwargs):
        self._env = simpy.RealtimeEnvironment()
        #self._env = simpy.Environment()
        
        kwargs["t"] = t

        #System-level data and control
        self._data = {(None, kw): kwargs[kw] for kw in kwargs}
        self._ctrl = dict()

        #Internal socket stuff
        context = zmq.Context.instance()
        self._zdata = context.socket(zmq.PAIR)
        self._zdata.connect("inproc://zdata")
        self._zctrl = context.socket(zmq.PAIR)
        self._zctrl.connect("inproc://zctrl")
        
    def init(self, prefix, **kwargs):
        """Initialize simulation data"""
        self.set({(prefix, kw): kwargs[kw] for kw in kwargs})

    def run(self):
        """Run!"""
        IOLoop.instance().add_callback(Thread(target=self._env.run).start)
        IOLoop.instance().start()
        
    def at(self, t):
        """Trigger at a specific tick"""
        name = "@{0:d}".format(t)
        
        if name not in self._ctrl:
            def wrapper():
                self._ctrl[(None, name)] = self._env.event()
                yield self._env.timeout(t - self._env.now)
                self._data[(None, "t")] = self._env.now
                self._ctrl[(None, name)].succeed()
                
        self._env.process(wrapper())
        
        return name
        
    def after(self, dt):
        """Trigger after a number of ticks"""
        name = "+{0:d}".format(dt)
        
        if name not in self._ctrl:
            def wrapper():
                self._ctrl[(None, name)] = self._env.event()
                yield self._env.timeout(dt)
                self._data[(None, "t")] = self._env.now
                self._ctrl[(None, name)].succeed()
                    
            self._env.process(wrapper())
        
        return name
        
    def every(self, dt, until=None):
        """Trigger every number of ticks"""
        name = "+{0:d}*".format(dt)
        
        if name not in self._ctrl:
            def wrapper():
                while until is None or self._env.now < until:
                    self._ctrl[(None, name)] = self._env.event()
                    yield self._env.timeout(dt)
                    self._data[(None, "t")] = self._env.now
                    self._ctrl[(None, name)].succeed()
                    
            self._env.process(wrapper())
        
        return name

    def get(self, keys):
        """Get data values"""
        return [self._data[k] for k in keys]

    def set(self, keys):
        """Set data values"""
        self._data.update(keys)
        
        self._zdata.send(dumps([{"key": k, "value": keys[k]} \
                                for k in keys]))#JSON

    def renew(self, keys):
        """Renew control events"""
        self._ctrl.update({k: self._env.event() for k in keys})

    def stop(self, keys):
        """Stop!"""
        return reduce(operator.__or__, [self._ctrl[k] for k in keys])

    def go(self, keys):
        """Go!"""
        map(simpy.Event.succeed, [self._ctrl[k] for k in keys])
        self.renew(keys)
        
        self._zctrl.send(dumps(keys))#JSON

    def process(self, func):
        """Inject process into system"""
        self._env.process(func())

class Process(object):
    """Simulation process"""

    def __init__(self, *conf):
        self._conf = [Config(*c) for c in conf]
    
    def __call__(self, func):
        self._func = coroutine(func)
              
        def caller(sys, *pres):
            """Replace function with process"""
            def wrapper():
                #Pull arguments from data values
                f = self._func(*sys.get([(pres[j],a) \
                                         for j,c in enumerate(self._conf) \
                                         for a in c.args]))

                #Create control events
                sys.renew([(pres[j],o) \
                           for j,c in enumerate(self._conf) \
                           for o in c.outs])

                while True:
                    #Only trigger on certain control events
                    yield sys.stop([(pres[j],i) \
                                    for j,c in enumerate(self._conf) \
                                    for i in c.ins])

                    try:
                        try:
                            #XXX this mess actually calls the function
                            sys.set((lambda d: \
                                     {(pres[j],p): d[k] \
                                      for k,(j,p) in enumerate([(j,p) \
                                                                for j,c in enumerate(self._conf) \
                                                                for p in c.pros])}) \
                                    (f.send(sys.get([(pres[j],r) \
                                                     for j,c in enumerate(self._conf) \
                                                     for r in c.reqs]))))
                        except Go as err:
                            #If using exceptions for control handling, restart function
                            f = self._func(*sys.get([(pres[j],a) \
                                                     for j,c in enumerate(self._conf) \
                                                     for a in c.args]))

                            raise err
                    except All:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs]#all the things!
                    except Many as err:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs
                                if (j,o) in err.value]#some of the things.
                    except One as err:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs
                                if (j,o) == err.value]#one of the things...
                    except No:
                        outs = []#nothing!
                    except:
                        outs = []#uh oh...
                        
                        raise
                    else:
                        outs = [(j,o) \
                                for j,c in enumerate(self._conf) \
                                for o in c.outs]#no exceptions used
                    finally:
                        sys.go([(pres[j],o) for j,o in outs])#no matter what
                    
            sys.process(wrapper)
            
        return caller