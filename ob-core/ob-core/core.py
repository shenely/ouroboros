import operator
import logging
import heqpq
import itertools

from .util import *

__all__ = ['Environment', 'System', 'Process']

class Environment(object):
    
    class Time(object):pass
    
    def __init__(self):
        self.q = []
        
    def run(self):
        while not self.q.empty():
            (p, f) = heapq.heappop(self.q)
            f.next()

class System(object):
    __metaclass__ = Memoize
    
    class Event(object):pass

    def __init__(self, env, name, items, procs):
        self.env = env
        
        self.name = name
        self.item = {item.name: {'data': item.data,
                                 'ctrl': {key: System.Event()
                                          for key in item.ctrl}}
                     for item in items}
        self.item.update({key: system.item[key[1:]]
                          for key in self.item
                          if key[0] == False
                          for system in System
                          if key[1] == system.name})
        all(system.item.update({key: self.item[key[1:]]
                                for key in self.item
                                if key[0] == False
                                and key[1] == self.name})
            for system in System)
        
        all(event.callbacks.append((lvl, func))
            for (lvl, func)
            in (Process[proc.name](system, *proc.item)
                for proc in procs)
            for event in func.next())
        
        System[self.name] = self

class Process(object):
    __metaclass__ = Memoize
    
    class Item(object):
        __slots__ = ('name', 'lvl',
                     'args', 'reqs', 'pros',
                     'evs', 'ins', 'outs')
        
        def __init__(self, name, lvl=0,
                     args=(), reqs=(), pros=(),
                     evs=(), ins=(), outs=()):
            self.name = name
            self.lvl = lvl
            
            self.args = args
            self.reqs = reqs
            self.pros = pros
            
            self.evs = evs
            self.ins = ins
            self.outs = outs

    def __init__(self, name, *items):
        self.name = name
        self.item = items
    
    def __call__(self, func):
        def wrapper(system, *items):
            """Replace function with process"""
            #Pull arguments and events from items
            args = (((system.item[name].data[key]
                      for key in self.item[n].args)
                     for name in item)
                    for n, item in enumerate(items))
            evs = (((system.item[name].ctrl[key]
                     for key in self.item[n].evs)
                    for name in item)
                   for n, item in enumerate(items))
            f = func(*args)
            yield evs
            
            try:
                yield 
                while True:
                    #XXX this mess actually calls the function
                    right = ((((system.item[name].data[key]
                                for key in self.item[n].reqs),
                               (system.item[name].ctrl[key]
                                for key in self.item[n].ins))
                              for name in item)
                             for n, item in enumerate(items))
                    left = f.send(right)
                    yield (((system.item[name].data.update
                             ({key: pro or system.item[name].data[key]
                               for key, pro in 
                               itertools.izip(self.item[n].pros, pros)}) or
                             (system.item[name].ctrl[key]
                              for key, out in
                              itertools.izip(self.item[n].outs, outs)
                              if outs))
                            for name, (pros, outs) in
                            itertools.izip(names, item))
                           for n, (names, item) in
                           enumerate(itertools.izip(items, left)))
            except StopIteration:
                return
            finally:
                pass
            
        return self.lvl, wrapper