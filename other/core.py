import operator
import heapq
import json

import simpy
import zmq
import zmq.eventloop.zmqstream
from bson import json_util

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

        context = zmq.Context.instance()

        socket = context.socket(zmq.PUB)
        self._pub = zmq.eventloop.zmqstream.ZMQStream(socket)
        self._pub.connect("tcp://127.0.0.1:5555")

        socket = context.socket(zmq.SUB)
        self._sub = zmq.eventloop.zmqstream.ZMQStream(socket)
        self._sub.connect("tcp://127.0.0.1:5556")
        self._sub.setsockopt(zmq.SUBSCRIBE,"data")
        self._sub.setsockopt(zmq.SUBSCRIBE,"ctrl")
        self._sub.on_recv(self.recv)
        
    def init(self,prefix,**kwargs):
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

    def send(self,addr,obj):
        if addr == "data":
            msg = json.dumps([{"key":o,"value":obj[o]} for o in obj],
                             default=json_util.default)
        elif addr == "ctrl":
            msg = json.dumps(obj,default=json_util.default)

        msgs = addr,msg

        self._pub.send_multipart(msgs)

    def recv(self,msgs):
        addr,msg = msgs

        obj = json.loads(msg,object_hook=json_util.object_hook)

        if addr == "data":
            self.update({tuple(o.key):o.value for o in obj})
        elif addr == "ctrl":
            self.trigger([tuple(o) for o in obj])

    def get(self,keys):
        return [self._data[k] for k in keys]

    def set(self,keys):
        self._data.update(keys)
        self.send("data",keys)

    def renew(self,keys):
        self._ctrl.update({k: self._env.event() for k in keys})

    def listen(self,keys):
        return reduce(operator.__or__,[self._ctrl[k] for k in keys])

    def trigger(self,keys):
        map(simpy.Event.succeed,[self._ctrl[k] for k in keys])
        self.send("ctrl",keys)

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
            f = self._func(*sys.get([(pres[a[0]],a[1]) for a in self._args]))
            
            def wrapper():
                sys.renew([(pres[o[0]],o[1]) for o in self._outs])

                while True:
                    yield sys.listen([(pres[i[0]],i[1]) for i in self._ins])

                    sys.set((lambda d: \
                             {(pres[self._pros[j][0]],self._pros[j][1]): d[j] \
                              for j in range(len(self._pros))})\
                            (f.send(sys.get([(pres[r[0]],r[1]) \
                                             for r in self._reqs]))))

                    sys.trigger([(pres[o[0]],o[1]) for o in self._outs])
                    
            sys.process(wrapper)
            
        return caller