#built-in libraries
import sys
import time
import types
import heapq
import logging

#external libraries
import tornado.ioloop
import tornado.gen

#internal libraries
from ouroboros import CATELOG
import ouroboros.lib as _

#constants
INFINITY = float('inf')

class Event(object):
    __slots__ = ('cbs',)
    def __init__(self, cbs=None):
        self.cbs = (cbs if cbs is not None else [])

@tornado.gen.coroutine
def main(*args):
    #first pass - initialize systems
    mem = {sys.pop('name'):
           {(True, None): sys}
           for sys in args}
    #second pass - populate internals
    any(mem[_id].setdefault(name, {}).update
        ({'data': item['data'],
          'ctrl': {key: Event()
                   for key in item['ctrl']}}
         if item is not None else {})
        for _id in mem for name, item in
        mem[_id][True, None].pop('mem').iteritems())
    #third pass - reference externals
    any(mem[_id].update
        ({name: mem[name[0]][False, name[1]]
          for name in mem[_id] if name[0] in mem})
        for _id in mem)
    #last pass - start processes
    any(ev.cbs.append((p, gen))
        for _id in mem for p, gen in
        ((p, wrap(mem[_id], maps, keys))
         for (p, wrap), maps, keys in
         ((CATELOG[proc['tag']],
           proc['map'], proc['key']) for proc in
          mem[_id][True, None].pop('exe')))
        for ev in gen.next())
    mem[None][True, None]['data']['m'] = mem#memory
    
    mem[None][True, None]['data']['e'] = e = set()#event set
    mem[None][True, None]['data']['q'] = q = []#task queue
    mem[None][False, None]['data']['z'] = z = []#clock time
    mem[None][True, None]['data']['t'] = T = time.time()#real time
    mem[None][False, None]['data']['t'] = t = - sys.float_info.epsilon#wall time
    
    #main loop
    loop = tornado.ioloop.IOLoop.current()
    heapq.heappush(z, (-INFINITY,
                       mem[None][False, None]['ctrl'][False]))#init event
    heapq.heappush(z, (0.0,
                       mem[None][False, None]['ctrl'][True]))#main event
    while True:
        any(e.add(heapq.heappop(z)[1])
            for _ in z if z[0][0] <= t)
        any(heapq.heappush(q, cb)
            for ev in e
            for cb in ev.cbs)#time event
        while len(q) > 0:
            (p, gen) = heapq.heappop(q)
            loop.add_callback(any, (heapq.heappush(z, (s, ev))
                                    if not isinstance(s, types.BooleanType)
                                    else any(heapq.heappush(q, cb)
                                             for cb in e.add(ev) or ev.cbs)
                                    if s is True else None
                                    for ev, s in gen.send(e)))
            yield
        else:e.clear()
        if len(z) > 0:
            T0, t0, x = (mem[None][True, None]['data']['t'],
                         mem[None][False, None]['data']['t'],
                         mem[None][False, None]['data']['x'])
            if x > 0.0:
                mem[None][False, None]['data']['t'] = t = z[0][0]#wall time
                mem[None][True, None]['data']['t'] = T = T0 + (t - t0) / x#real time
                yield tornado.gen.sleep(T - time.time())
            else:
                mem[None][True, None]['data']['t'] = time.time()#real time
                yield
        else:break

if __name__ == '__main__':
    loop = tornado.ioloop.IOLoop.current().run_sync(main)
