import operator
import heapq

import simpy

def coroutine(func):
    def wrapper(*args,**kwargs):
        gen = func(*args,**kwargs)
        gen.next()
        return gen
    
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    
    return wrapper

class System(object):
    def __init__(self,t=0,**kwargs):
        self._env = simpy.Environment()
        
        kwargs["t"] = t
        
        self._data = {(None,kw):kwargs[kw] for kw in kwargs}
        self._ctrl = dict()
        
        self._clock = [self._data[(None,"t")]]
        self.clock()
        
    def set(self,prefix,**kwargs):
        self._data.update({(prefix,kw):kwargs[kw] for kw in kwargs})
        
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
            f = self._func(*[sys._data[(pres[a[0]],a[1])] \
                             for a in self._args])
            
            def wrapper():
                while True:
                    sys._ctrl.update({(pres[o[0]],o[1]): sys._env.event() \
                                      for o in self._outs})
                    
                    yield reduce(operator.__or__,
                                 [sys._ctrl[(pres[i[0]],i[1])] \
                                  for i in self._ins])
                    
                    sys._data.update((lambda d: \
                                      {(pres[self._pros[j][0]],self._pros[j][1]): d[j] \
                                       for j in range(len(self._pros))})\
                                     (f.send([sys._data[(pres[r[0]],r[1])] \
                                              for r in self._reqs])))
                    
                    map(simpy.Event.succeed,
                        [sys._ctrl[(pres[o[0]],o[1])] \
                         for o in self._outs])
                    
            sys._env.process(wrapper())
            
        return caller