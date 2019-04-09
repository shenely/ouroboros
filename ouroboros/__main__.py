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
import argparse
import logging

# external libraries
import tornado.gen
import tornado.web
import tornado.websocket
import tornado.concurrent
import tornado.ioloop

# internal libraries
from ouroboros import default, object_hook, Item, run
import ouroboros.ext as _

# constants
MILLI = 1e-3
INFINITY = float("inf")
UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)

# priorities
CRITICAL = 1
HIGH     = 10
NORMAL   = 100
LOW      = 1000
TRIVIAL  = 10000

logging.basicConfig(format="(%(asctime)s) [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SL",
                    level=logging.DEBUG)


def parse_time(s):
    assert isinstance(s, types.StringTypes)
    if s.lower() == "now":
        t = time.time()
    elif s.isdigit():
        t = int(s)
    else:
        dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
        t = int((dt - UNIX_EPOCH).total_seconds() / MILLI)
    return t


def parse_rate(s):
    assert isinstance(s, types.BaseString)
    if s.lower() in "rt":
        x = 1.0
    else:
        x = float(x)
        assert x > 0.0
    return x
    

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
        s = json.dumps(obj, default=default)
        self.write(s)

    def put(self, _id, name):
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
        item = self.lake[_id][False, name]
        item["data"].update({pair["key"]: pair["value"]
                             for pair in obj
                             if pair["key"] in item.data})


class CtrlHandler(ObRequestHandler):

    def post(self, _id, name):
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
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
            obj = [{"name": _id,
                    "items": [{"key": name[1],
                               "data": [{"key": key, "value": value}
                                        for (key, value)
                                        in item.data.iteritems()],
                               "ctrl": [{"key": key, "value": ev in e}
                                        for (key, ev)
                                        in item.ctrl.iteritems()]}
                              for (name, item)
                              in model[True, None].iteritems()
                              if name[0] is False]}
                   for (_id, model) in self.lake.iteritems()
                   if name is not None]
        s = json.dumps(obj, default=default)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time", type=parse_time, default=0.0)
    parser.add_argument("-x", "--rate", type=parse_rate, default=1.0)
    parser.add_argument("filename")
    ns = parser.parse_args()
    
    with open(ns.filename, "rb") as pkl:
        sim = pickle.load(pkl)
        
        # first pass - populate internals
        lake = {model["name"]: {name: (Item(**item)
                                       if item is not None
                                       else None)
                                for (name, item)
                                in model["items"].iteritems()}
                for model in sim}
        logging.debug("done 1st pass")
        
        # second pass - reference externals
        any(lake[_id].update({name: lake[name[0]].get((False, name[1]))
                              for name in lake[_id].iterkeys()
                              if name[0] in lake})
            for _id in lake)
        logging.debug("done 2nd pass")
        
        # third pass - start tasks
        tasks = tuple(run(task, lake[model["name"]])
                      for model in sim
                      for task in model["procs"])
        logging.debug("done 3rd pass")

    lake[None][False, None].data["t"] = ns.time
    lake[None][False, None].data["x"] = ns.rate
    
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
