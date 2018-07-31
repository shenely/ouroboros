#built-in libraries
import sys
import time
import datetime
import functools
import types
import heapq
import json
import pickle
import logging

#external libraries
import pytz
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import tornado.concurrent

#internal libraries
from ouroboros import CATELOG, REGISTRY
import ouroboros.ext as _

#constants
INFINITY = float('inf')
UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

logging.basicConfig(format='[%(levelname)s] (%(asctime)s) %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%SL',
                    level=logging.DEBUG)

def default(obj):
    key, default = REGISTRY.get(type(obj))
    if default is not None:
        dct = {key: default(obj)}
        return dct
    else:raise TypeError

def object_hook(dct):
    object_hook = REGISTRY.get(dct.iterkeys().next())
    if object_hook is not None:
        obj = object_hook(dct.getvalues().next())
        return obj
    else:return dct

class Event(object):
    __slots__ = ('cbs',)
    def __init__(self, cbs=None):
        self.cbs = (cbs if cbs is not None else [])

class ObRequestHandler(tornado.web.RequestHandler):

    def initialize(self, mem):
        self.mem = mem

class FlagHandler(ObRequestHandler):
        
    def post(self):
        d = self.mem[None][True, None]['data']
        if d['f'].done():#pause
            d['f'] = tornado.concurrent.Future()
        else:#resume
            d['t'] = time.time()#real time
            d['f'].set_result(True)

class InfoHandler(ObRequestHandler):
        
    def get(self):
        d = self.mem[None][True, None]['data']
        obj = {'e': len(d['e']),
               'q': len(d['q']),
               'z': len(d['z']),
               'f': d['f'].done()}
        s = json.dumps(obj)
        self.write(s)

class DataHandler(ObRequestHandler):
        
    def get(self, name, tag):
        item = self.mem[name][False, tag]
        obj = [{'key': key,
                'value': value}
               for (key, value)
               in item['data'].iteritems()]
        s = json.dumps(obj, default=default)
        self.write(s)

    def put(self, name, tag):
        item = self.mem[name][False, tag]
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
        item['data'].update({pair['key']: pair['value']
                             for pair in obj
                             if pair['key'] in item['data']})

class CtrlHandler(ObRequestHandler):

    def post(self, name, tag):
        e = self.mem[None][True, None]['data']['e']
        item = self.mem[name][False, tag]
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
        any(e.add(item['ctrl'][pair['key']])
            for pair in obj
            if pair['value'] is True
            and pair['key'] in item['ctrl'])

class StreamHandler(tornado.websocket.WebSocketHandler,
                    ObRequestHandler):
        
    def on_pong(self, stream, address):
        d = self.mem[None][True, None]['data']
        if d['f'].done():
            e = d['e']
            obj = [{'name': name,
                    'items': [{'key': tag[1],
                               'data': [{'key': key,
                                         'value': value}
                                        for (key, value)
                                        in item['data'].iteritems()],
                               'ctrl': [{'key': key,
                                         'value': ev in e}
                                        for (key, ev)
                                        in item['ctrl'].iteritems()]}
                              for (tag, item) in sys.iteritems()
                              if tag[0] is False]}
                   for (name, sys) in self.mem.iteritems()
                   if name is not None]
        s = json.dumps(obj, default=default)
        self.write_message(s)
    
@tornado.gen.coroutine
def main(mem, loop):
    """main loop"""
    mem[None][True, None]['data']['e'] = e = set()#event set
    mem[None][True, None]['data']['q'] = q = []#task queue
    mem[None][True, None]['data']['z'] = z = []#clock time
    mem[None][True, None]['data']['f'] = tornado.concurrent.Future()

    t = mem[None][False, None]['data']['t']#wall time
    heapq.heappush(z, (-INFINITY,#init event
                       mem[None][False, None]['ctrl'][False]))
    heapq.heappush(z, (t + sys.float_info.epsilon,#main event
                       mem[None][False, None]['ctrl'][True]))
        
    while True:
        yield mem[None][True, None]['data']['f']
        any(e.add(heapq.heappop(z)[1])
            for _ in z if z[0][0] <= t)
        any(heapq.heappush(q, cb)
            for ev in e
            for cb in ev.cbs)#time event
        while len(q) > 0:
            (p, gen) = heapq.heappop(q)
            #XXX controls events and callbacks
            #... events may only occur once per clock cycle
            #... one instance of callback may be in queue
            #... bool events add callbacks to queue
            #... truthy events are recorded
            #... falsey events are not recorded
            #... numeric events are added to clock
            loop.add_callback(any, (heapq.heappush(z, (s, ev))
                                    if not isinstance(s, types.BooleanType)
                                    else (any(heapq.heappush(q, cb)
                                              for cb in ev.cbs
                                              if cb not in q)
                                          if ev not in e else None)
                                    or (e.add(ev) if s is True else None)
                                    for ev, s in gen.send(e)))
            yield
        else:e.clear()
        T, t0, x = (mem[None][True, None]['data']['t'],
                    mem[None][False, None]['data']['t'],
                    mem[None][False, None]['data']['x'])
        logging.debug('exec time:%.4f', time.time() - T)
        if len(z) > 0 and x > 0.0:
            t = z[0][0]#wall time
            T += (t - t0) / x#real time
            yield tornado.gen.sleep(T - time.time())
            logging.debug('wall time:%.4f', t)
        else:
            T = time.time()#real time
            mem[None][True, None]['data']['f'] = tornado.concurrent.Future()
        mem[None][True, None]['data']['t'] = T#real time
        mem[None][False, None]['data']['t'] = t#wall time

if __name__ == '__main__':
    with open('test.pkl', 'rb') as pkl:
        #first pass - initialize systems
        mem = {sys.pop('name'):
               {(True, None): sys}
               for sys in pickle.load(pkl)}
        logging.debug('done 1st pass')
        
        #second pass - populate internals
        any(mem[_id].setdefault(name, {}).update
            ({'data': item['data'],
              'ctrl': {key: Event()
                       for key in item['ctrl']}}
             if item is not None else {})
            for _id in mem for name, item in
            mem[_id][True, None].pop('mem').iteritems())
        logging.debug('done 2nd pass')
        
        #third pass - reference externals
        any(mem[_id].update
            ({name: mem[name[0]][False, name[1]]
              for name in mem[_id] if name[0] in mem})
            for _id in mem)
        logging.debug('done 3rd pass')
        
        #last pass - start processes
        any(ev.cbs.append((p, gen))
            for _id in mem for p, gen in
            ((p, wrap(mem[_id], maps, keys))
             for (p, wrap), maps, keys in
             ((CATELOG[proc['tag']],
               proc['map'], proc['key']) for proc in
              mem[_id][True, None].pop('exe')))
            for ev in gen.next())
        logging.debug('done 4th pass')
    
    loop = tornado.ioloop.IOLoop.current()
    app = (tornado.web.Application
           ([(r'/ob-rest-api/flag', FlagHandler, {'mem': mem}),
             (r'/ob-rest-api/info', InfoHandler, {'mem': mem}),
             (r'/ob-rest-api/data/(\w+)/(\w+)', DataHandler, {'mem': mem}),
             (r'/ob-rest-api/ctrl/(\w+)/(\w+)', CtrlHandler, {'mem': mem}),
             (r'/ob-io-stream/', StreamHandler, {'mem': mem})],
            websocket_ping_interval=1))
    app.listen(8888)
    loop.run_sync(functools.partial(main, mem, loop))
