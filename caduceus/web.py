<<<<<<< HEAD
import math
import httplib
import datetime

import numpy
import simpy.core
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.concurrent

from core import System, Process
from util import loads, dumps
import clock, vec, geo, orb

EARTH_RADIUS = 6378.1370
EARTH_FLATTENING = 1 / 298.257223563
EARTH_GRAVITATION = 398600.4418

J2000 = datetime.datetime(2000,1,1,12)#Julian epoch (2000-01-01T12:00:00Z)

SECOND = datetime.timedelta(seconds=1)
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

#Unit vectors
O = numpy.array([0,0,0])
I = numpy.array([1,0,0])
J = numpy.array([0,1,0])
K = numpy.array([0,0,1])

"""
GET /caduceus.py -> CaduceusHandler.get
GET /caduceus.py?name=<name> -> CaduceusHandler.get
POST /caduceus.py (config) -> CaduceusHandler.post
DELETE /caduceus.py?name=<name> -> CaduceusHandler.delete
WS /caduceus.py/system/<name> -> CaduceusWebSocket.open
"""

configs = [
    {
        "name": "test",
        "time": {
            "at": [ ],
            "after": [ 0 ],
            "every": [ 1 ]
        },
        "data": [
            {
                "name": None,
                "args": [
                    { "key": "t_dt", "value": J2000 },
                    { "key": "dt_td", "value": SECOND }
                ]
            },
            {
                "name": "earth",
                "args": [
                    { "key": "mu", "value": EARTH_GRAVITATION },
                    { "key": "f", "value": EARTH_FLATTENING },
                    { "key": "R_km", "value": EARTH_RADIUS }
                ]
            },
            {
                "name": "geo.mtv",
                "args": [
                    { "key": "r", "value": 0.032 },
                    { "key": "az", "value": math.radians(-122-(4.0-55.0/60)/60) },
                    { "key": "el", "value": math.radians(37+(23.0+22.0/60)/60) },
                    { "key": "r_t", "value": 0 },
                    { "key": "az_t", "value": 0 },
                    { "key": "el_t", "value": 0 }
                ]
            },
            {
                "name": "orb.iss",
                "args": [
                    { "key": "line1", "value": "1 25544U 98067A   00160.86541705 -.00081986  00000-0 -12286-2 0  9995" },
                    { "key": "line2", "value": "2 25544  51.6431  99.5383 0000357 151.8232 309.6472 15.54475098  3693" },
                ]
            },
            { "name": "iss.apse", "args": [ { "key": "_t_bar", "value": O } ] },
            { "name": "iss.pole", "args": [{ "key": "_t_bar", "value": O } ] }
        ],
        "ctrl": [
            { "name": "clock.clock", "args": [ None ] },
            { "name": "geo.sidereal", "args": [ None, "orb.iss" ] },
            { "name": "orb.simple", "args": [ None, "orb.iss" ] },
            { "name": "orb.rec2orb", "args": [ "earth", "orb.iss", "iss.apse", "iss.pole" ] },
            { "name": "vec.fun2obl", "args": [ "iss.apse", "iss.pole", "orb.iss", "iss.pqw" ] },
            { "name": "vec.rec2sph", "args": [ "iss.pqw" ] },
            { "name": "vec.rec2sph", "args": [ "iss.apse" ] },
            { "name": "vec.rec2sph", "args": [ "iss.pole" ] },
            { "name": "orb.sph2kep", "args": [ "iss.pqw", "iss.apse", "iss.pole", "iss.kep" ] },
        ]
    },
    {
        "name": "slow-clock",
        "time": {
            "at": [ ],
            "after": [ ],
            "every": [ 1 ]
        },
        "data": [
            {
                "name": None,
                "args": [
                    { "key": "t_dt", "value": J2000 },
                    { "key": "dt_td", "value": MINUTE }
                ]
            },
        ],
        "ctrl": [
            { "name": "clock.clock", "args": [ None ] }
        ]
    },
    {
        "name": "fast-clock",
        "time": {
            "at": [ ],
            "after": [ ],
            "every": [ 1 ]
        },
        "data": [
            {
                "name": None,
                "args": [
                    { "key": "t_dt", "value": J2000 },
                    { "key": "dt_td", "value": HOUR }
                ]
            },
        ],
        "ctrl": [
            { "name": "clock.clock", "args": [ None ] }
        ]
    }
]
message = dumps(configs)

class CaduceusHandler(tornado.web.RequestHandler):
    
    def initialize(self, _):
        self._ = _
        
    def get(self, which):
        try:
            name = self.get_query_argument("name")
            data = System[name]._config
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            data = {"system":[{"name":name,
                               "config":System[name]._config}
                              for name in System],
                    "process":[{"name":name,
                                "config":[config._asdict()
                                          for config in Process[name]]}
                               for name in Process]}
            status = httplib.OK
        else:
            data = None
            status = httplib.NOT_FOUND
        finally:
            self.write(dumps(data))
            self.set_status(status)
        
    def post(self):
        try:
            self._.start(loads(self.get_body_argument("config")))
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        else:
            status = httplib.NOT_FOUND
        finally:
            self.set_status(status)
        
    def delete(self, which):
        try:
            self._.stop(self.get_query_argument("name"))
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        else:
            status = httplib.NOT_FOUND
        finally:
            self.set_status(status)

class CaduceusWebSocket(tornado.websocket.WebSocketHandler):
    
    def open(self, which, name):
        self._sys = System[name]
        
        self._sys.on_set(self._on_data)
        self._sys.on_go(self._on_ctrl)

    def on_close(self):
        self._sys.unwatch(self._on_data)
        self._sys.unlisten(self._on_ctrl)

    def on_message(self, message):
        packet = loads(message)
        
        if "data" in packet:
            self._sys.set(packet["data"])
        if "ctrl" in packet:
            self._sys.go(packet["ctrl"])

    def _on_data(self, packet):        
        self.write_message(dumps({"data": packet}))

    def _on_ctrl(self, packet):
        self.write_message(dumps({"ctrl": packet}))
        
class Caduceus(object):
    
    def __init__(self):
        self._env = simpy.RealtimeEnvironment(strict=False)
        self._loop = tornado.ioloop.IOLoop.current()
        
        def wrapper(future):
            def caller():
                try:
                    self._env.step()
                    self._loop.add_callback(caller)
                except simpy.core.EmptySchedule:
                    return
            self._loop.add_callback(caller)
        
        self._future = tornado.concurrent.Future()
        self._future.add_done_callback(wrapper)
        
    def start(self, config):
        self._loop.add_callback(System, self._env, config)
        if not self._future.done():self._future.set_result(True)
        
    def stop(self, name):
        self._loop.add_callback(System[name].halt)

    def run(self):
        self._loop.start()

def main():
    configs = loads(message)

    _ = Caduceus()
    
    _.start(configs[0])
    _.start(configs[1])
    _.start(configs[2])
    
    _.run()
        
    
    app = tornado.web.Application([(r"/caduceus.py", CaduceusHandler, {"_": _}),
                                   (r"/caduceus.py/(.*)", CaduceusWebSocket),
                                   (r'/(.*)', tornado.web.StaticFileHandler,
                                    {"path": "static",
                                     "default_filename": "inde(\w*)/(\w*)x.html"})])
    app.listen(8000)
=======
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop import ioloop

ioloop.install()

from tornado.web import StaticFileHandler,Application
from tornado.websocket import WebSocketHandler

class ZMQWebSocket(WebSocketHandler):
    def __init__(self,*args,**kwargs):
        self._socket = kwargs.pop("socket")

        super(ZMQWebSocket,self).__init__(*args,**kwargs)

    def open(self):
        self._stream = ZMQStream(self._socket)
        self._stream.on_recv(self.recv)

    def on_close(self):
        self._stream.close()

    def on_message(self,msg):
        self._stream.send(msg)

    def recv(self,msgs):
        msg = msgs[0]

        self.write_message(msg)

def main():
    context = zmq.Context.instance()

    data = context.socket(zmq.PAIR)
    data.bind("inproc://zdata")

    ctrl = context.socket(zmq.PAIR)
    ctrl.bind("inproc://zctrl")

    app = Application([(r"/data",ZMQWebSocket, {"socket": data}),
                       (r'/static/(.*)', StaticFileHandler, {"path": "static"})])
    app.listen(8080)
>>>>>>> branch 'master' of https://github.com/shenely/ouroboros.git

if __name__ == '__main__':
    main()