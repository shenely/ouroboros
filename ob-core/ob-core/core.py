import operator
import collections
import logging

import simpy

from .util import *

__all__ = ["Config", "System", "Process"]

Config = collections.namedtuple("Config",
                                ["args", "ins", "outs", "reqs", "pros"])

class System(object):
    __metaclass__ = Memoize

    def __init__(self, env, config):
        self._env = env
        
        self._name = config["name"]
        self._config = config
        
        self._active = []
        
        #Time configuration
        self._data = {(None, "t"): self._env.now}
        self._ctrl = {(None, self.at(0)): self._env.event(),
                      (None, self.every(1)): self._env.event()}
        
        #Everything else
        self._data.update({(data["name"], arg["key"]): arg["value"]
                           for data in config["data"]
                           for arg in data["args"]})
        for name in System:
            #Copy data to child systems
            System[name]._data.update({((True,) + key[1:]): self._data[key]
                                       for key in self._data
                                       if key[0] == name})
            #Copy data from parent systems
            self._data.update({((name,) + key[1:]): System[name]._data[key]
                               for key in System[name]._data
                               if key[0] == True})
            
        self._ctrl.update({out: self._env.event()
                           for ctrl in config["ctrl"]
                           for out in Process[ctrl["name"]]._caller
                           (self, *ctrl["args"])})
        for name in System:
            #Copy controls to child systems
            System[name]._ctrl.update({((True,) + key[1:]):
                                       System[name]._ctrl.get((True,) + key[1:],
                                                              self._env.event())
                                       for key in self._ctrl
                                       if key[0] == name})
            #Copy controls from parent systems
            self._ctrl.update({((name,) + key[1:]):
                               self._ctrl.get((name,) + key[1:],
                                              self._env.event())
                               for key in System[name]._ctrl
                               if key[0] == True})
        
        self._eyes = []
        self._ears = []
        
        System[self._name] = self
        
    def at(self, t):
        """Trigger at a specific tick"""
        name = "@{0:d}".format(t)
        
        def wrapper():
            try:
                self._ctrl[(None, name)] = self._env.event()
                yield self._env.timeout(t - self._env.now)
                self._data[(None, "t")] = self._env.now
                self._ctrl[(None, name)].succeed()
            except simpy.Interrupt:
                return
            finally:
                self.kill(process)
                
        process = self.spawn(wrapper)
        return name
        
    def after(self, dt):
        """Trigger after a number of ticks"""
        name = "+{0:d}".format(dt)
        
        def wrapper():
            try:
                self._ctrl[(None, name)] = self._env.event()
                yield self._env.timeout(dt)
                self._data[(None, "t")] = self._env.now
                self._ctrl[(None, name)].succeed()
            except simpy.Interrupt:
                return
            finally:
                self.kill(process)
                
        process = self.spawn(wrapper)
        return name
        
    def every(self, dt, until=None):
        """Trigger every number of ticks"""
        name = "+{0:d}*".format(dt)
        
        def wrapper():
            try:
                while until is None or self._env.now < until:
                    self._ctrl[(None, name)] = self._env.event()
                    yield self._env.timeout(dt)
                    self._data[(None, "t")] = self._env.now
                    self._ctrl[(None, name)].succeed()
            except simpy.Interrupt:
                return
            finally:
                self.kill(process)
                
        process = self.spawn(wrapper)
        return name

    def get(self, keys):
        """Get some values"""
        return [self._data[key]
                for key in keys]

    def set(self, dct):
        """Set some values"""
        self._data.update(dct)
        [eye(self._name, dct) for eye in self._eyes]
        for name in System:
            if name != self._name:
                #Set some data if...
                mapping = {((True,) + key[1:]): dct[key]#...child
                           for key in dct
                           if key[0] == name}
                mapping.update({key: dct[(True,) + key[1:]]#...parent
                                for key in System[name]._data
                                if key[0] == self._name
                                and (True,) + key[1:] in dct})
                if mapping:
                    System[name]._data.update(mapping)
                    [eye(name, mapping)
                     for eye in System[name]._eyes]

    def stop(self, keys):
        """Stop!"""
        return reduce(operator.__or__, [self._ctrl[key]
                                        for key in keys])

    def go(self, keys):
        """Go!"""
        map(simpy.Event.succeed, [self._ctrl[key]
                                  for key in keys])
        [ear(self._name, keys)
         for ear in self._ears]
        self._ctrl.update({key: self._env.event()
                           for key in keys})
        for name in System:
            if name != self._name:
                #Fire some controls if...
                mapping = (set([(True,) + key[1:]#...child
                                for key in keys
                                if key[0] == name]) |
                           set([key#...parent
                                for key in System[name]._ctrl
                                if key[0] == self._name
                                and (True,) + key[1:] in keys]))
                if mapping:
                    map(simpy.Event.succeed, [System[name]._ctrl[key]
                                              for key in mapping])
                    [ear(self._name, list(mapping))
                     for ear in System[name]._ears]
                    System[name]._ctrl.update({key: self._env.event()
                                               for key in mapping})

    def spawn(self, func):
        """Spawn new process"""
        process = self._env.process(func())
        self._active.append(process)
        return process
        
    def kill(self, process):
        self._active.remove(process)
        
    def watch(self, callback):
        self._eyes.append(callback)
    def unwatch(self, callback):
        self._eyes.remove(callback)
    def listen(self, callback):
        self._ears.append(callback)
    def unlisten(self, callback):
        self._ears.remove(callback)
        
    def halt(self):
        [process.interrupt()
         for process in self._active]

class Process(object):
    __metaclass__ = Memoize

    def __init__(self, name, *config):
        self._name = name
        self._config = [Config(*c) for c in config]
    
    def __call__(self, func):        
        self._func = coroutine(func)
              
        def caller(sys, *pres):
            """Replace function with process"""
            def wrapper():
                #Pull arguments from data values
                f = self._func(*sys.get([(pres[j], a)
                                         for (j, c) in enumerate(self._config)
                                         for a in c.args]))

                try:
                    while True:
                        #Only trigger on certain control events
                        yield sys.stop([(pres[j], i) \
                                        for (j, c) in enumerate(self._config)
                                        for i in c.ins])

                        try:
                            try:
                                #XXX this mess actually calls the function
                                sys.set((lambda d:
                                         {(pres[j], p): d[k]
                                          for (k, (j, p)) in enumerate([(j, p)
                                                                    for (j, c) in enumerate(self._config)
                                                                    for p in c.pros])})
                                        (f.send(sys.get([(pres[j], r)
                                                         for (j, c) in enumerate(self._config)
                                                         for r in c.reqs]))))
                            except Go as err:
                                #If using exceptions for control handling, restart function
                                f = self._func(*sys.get([(pres[j],a)
                                                         for (j, c) in enumerate(self._config)
                                                         for a in c.args]))
    
                                raise err
                        except All:#all the things!
                            outs = [(j, o)
                                    for (j, c) in enumerate(self._config)
                                    for o in c.outs]
                        except Many as err:#some of the things.
                            outs = [(j, o) \
                                    for (j, c) in enumerate(self._config)
                                    for o in c.outs
                                    if (j, o) in err.value]
                        except One as err:#one of the things...
                            outs = [(j, o)
                                    for (j, c) in enumerate(self._config)
                                    for o in c.outs
                                    if (j, o) == err.value]
                        except No:#nothing!
                            outs = []
                        except StopIteration:#oh, ok
                            outs = []
                        except:#uh oh...
                            outs = []
                            raise
                        else:#keep calm...
                            outs = [(j, o)
                                    for (j, c) in enumerate(self._config)
                                    for o in c.outs if c.outs[o]]
                        finally:#...and carry on
                            sys.go([(pres[j], o) for (j, o) in outs])
                except simpy.Interrupt:
                    return
                finally:
                    sys.kill(process)
                    
            process = sys.spawn(wrapper)
            
            return [(pres[j], o) 
                    for (j, c) in enumerate(self._config)
                    for o in c.outs]
        
        print self._name
        self._caller = caller
        Process[self._name] = self
            
        return caller