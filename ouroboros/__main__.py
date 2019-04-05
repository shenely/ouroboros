# built-in libraries
import sys
import time
import datetime
import collections
import functools
import itertools
import types
import heapq
import json
import pickle
import logging

# external libraries
import pytz
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import tornado.concurrent

# internal libraries
from ouroboros import (Item, run, encoder, decoder)
import ouroboros.ext as _

# constants
INFINITY = float("inf")
UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

# priorities
CRITICAL = 1
HIGH     = 10
NORMAL   = 100
LOW      = 1000
TRIVIAL  = 10000

logging.basicConfig(format="(%(asctime)s) [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SL",
                    level=logging.DEBUG)
    

class ObRequestHandler(tornado.web.RequestHandler):

    def initialize(self, lake):
        self.lake = lake


class FlagHandler(ObRequestHandler):
        
    def post(self):
        d = self.lake[None][True, None].data
        if d["f"].done():  # pause
            d["f"] = tornado.concurrent.Future()
        else:  # resume
            d["t"] = time.time()  # real time
            d["f"].set_result(True)


class InfoHandler(ObRequestHandler):
        
    def get(self):
        d = self.lake[None][True, None].data
        obj = {"e": len(d["e"]),
               "q": len(d["q"]),
               "z": len(d["z"]),
               "f": d["f"].done()}
        s = json.dumps(obj)
        self.write(s)


class DataHandler(ObRequestHandler):
        
    def get(self, _id, name):
        item = self.lake[_id][False, name]
        obj = [{"key": key,
                "value": value}
               for (key, value)
               in item.data.iteritems()]
        s = encoder.dumps(obs)
        self.write(s)

    def put(self, _id, name):
        s = self.request.body
        obj = decoder.loads(s)
        item = self.lake[_id][False, name]
        item["data"].update({pair["key"]: pair["value"]
                             for pair in obj
                             if pair["key"] in item.data})


class CtrlHandler(ObRequestHandler):

    def post(self, _id, name):
        s = self.request.body
        obj = decoder.loads(s)
        e = self.lake[None][True, None].data["e"]
        item = self.lake[_id][False, name]
        any(e.add(item.data[pair["key"]])
            for pair in obj
            if pair["value"] is True
            and pair["key"] in item.ctrl)

class StreamHandler(tornado.websocket.WebSocketHandler,
                    ObRequestHandler):
        
    def on_pong(self, io, addr):
        d = self.lake[None][True, None].data
        if d["f"].done():
            e = d["e"]
            obj = [{"_id": _id,
                    "items": [{"key": name[1],
                               "data": [{"key": key, "value": value}
                                        for (key, value)
                                        in item.data.iteritems()],
                               "ctrl": [{"key": key, "value": ev in e}
                                        for (key, ev)
                                        in item.ctrl.iteritems()]}
                              for (name, item) in model[True, None].iteritems()
                              if name[0] is False]}
                   for (_id, model) in self.lake.iteritems()
                   if name is not None]
        s = encoder.dumps(obj)
        self.write_message(s)

    
@tornado.gen.coroutine
def main(pool, loop):
    """main loop"""
    pool[True, None].data["e"] = e = set()  # event set
    pool[True, None].data["q"] = q = collections.deque()  # task queue
    pool[True, None].data["z"] = z = []  # clock time
    pool[True, None].data["f"] = tornado.concurrent.Future()

    any(task.gen.send(e)
        for task in tasks)

    t = pool[False, None].data["t"]  # wall time
    heapq.heappush(z, (-INFINITY,  # init event
                       pool[False, None].ctrl[False]))
    heapq.heappush(z, (t + sys.float_info.epsilon,  # main event
                       pool[False, None].ctrl[True]))
        
    while True:
        yield pool[True, None].data["f"]
        any(e.add(heapq.heappop(z)[1])
            for _ in z
            if z[0][0] <= t)
        any(q.append(cb)
            for ev in e
            for cb in ev.cbs)  # time event
        while len(q) > 0:
            task = q.popleft()
            # XXX controls events and callbacks
            # ... events may only occur once per clock cycle
            # ... one instance of callback may be in queue
            # ... bool events add callbacks to queue
            # ... truthy events are recorded
            # ... falsey events are not recorded
            # ... numeric events are added to clock
            loop.add_callback(any, (
                heapq.heappush(z, (s, ev))
                if not isinstance(s, types.BooleanType)
                else (any(q.append(cb)
                          for cb in ev.cbs)
                      if ev not in e
                      else None)
                or (not s or e.add(ev))
                for (ev, s) in itertools.chain(*task.gen.send(e))))
            yield
        else:e.clear()
        T, t0, x = (pool[True, None].data["t"],
                    pool[False, None].data["t"],
                    pool[False, None].data["x"])
        logging.debug("exec time: %.4f", time.time() - T)
        if len(z) > 0 and x > 0.0:
            t = z[0][0]  # wall time
            T += (t - t0) / x  # real time
            yield tornado.gen.sleep(T - time.time())
            logging.debug("wall time: %.4f", t)
        else:
            T = time.time()  # real time
            pool[True, None].data["f"] = tornado.concurrent.Future()
        pool[True, None].data["t"] = T  # real time
        pool[False, None].data["t"] = t  # wall time

if __name__ == "__main__":
    with open("test.pkl", "rb") as pkl:
        # first pass - initialize models
        sim = pickle.load(pkl)
        logging.debug("done 1st pass")
        
        # second pass - populate internals
        lake = {model["name"]: {name: (Item(**item)
                                       if item is not None
                                       else None)
                                for (name, item)
                                in model["items"].iteritems()}
                for model in sim}
        logging.debug("done 2nd pass")
        
        # third pass - reference externals
        any(lake[_id].update({name: lake[name[0]].get((False, name[1]))
                              for name in lake[_id].iterkeys()
                              if name[0] in lake})
            for _id in lake)
        logging.debug("done 3rd pass")
        
        # fourth pass - start tasks
        tasks = tuple(run(task, lake[model["name"]])
                      for model in sim
                      for task in model["procs"])
        logging.debug("done 4th pass")
    
    loop = tornado.ioloop.IOLoop.current()
    app = tornado.web.Application([
        (r"/ob-rest-api/flag", FlagHandler, {"lake": lake}),
        (r"/ob-rest-api/info", InfoHandler, {"lake": lake}),
        (r"/ob-rest-api/data/(\w+)/(\w+)", DataHandler, {"lake": lake}),
        (r"/ob-rest-api/ctrl/(\w+)/(\w+)", CtrlHandler, {"lake": lake}),
        (r"/ob-io-stream/", StreamHandler, {"lake": lake})
        ], websocket_ping_interval=1)
    app.listen(8888)
    loop.run_sync(functools.partial(main, lake[None], loop))
