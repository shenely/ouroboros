#built-in libraries
import heapq

#external libraries
#...

#internal libraries
from ouroboros import CATELOG
import ouroboros.lib as _

class Event(object):
    __slots__ = ('cbs',)
    def __init__(self, cbs=None):
        self.cbs = (cbs if cbs is not None else [])

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
        mem[_id][True, None].pop('items').iteritems())
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
           proc['maps'], proc['keys']) for proc in
          mem[_id][True, None].pop('procs')))
        for ev in gen.next())
    mem[None][True, None]['data'][True] = mem#memory
    
    #main loop
    q = mem[None][True, None]['data']['q']#task queue
    e = mem[None][True, None]['data']['e']#event set
    any(heapq.heappush(q, cb) for cb in
        mem[None][False, None]['ctrl'][None].cbs)#init event
    while len(q) > 0:
        (p, gen) = heapq.heappop(q)
        any(heapq.heappush(q, cb)
            for ev in gen.send(e)
            if ev not in e
            for cb in e.add(ev) or ev.cbs
            if cb not in q)

if __name__ == '__main__':
    a = Event(cbs=[])
    print hash(a)
    main()
