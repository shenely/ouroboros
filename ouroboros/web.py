import os.path
import math
import httplib
import datetime
import logging

import numpy
import tornado.web
import tornado.websocket
import tornado.ioloop

from . import Ouroboros
from .util import loads, dumps, default, TornadoEnvironment

logging.basicConfig()

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
/ob-rest-api/

system/ -> SystemHandler
GET -> SystemHandler.get {data: [String, ...]}
{data: [Object, ...]}
GET ?name=<name> -> SystemHandler.get {data: Object}
POST {data: Object} -> SystemHandler.post
DELETE ?name=<name> -> SystemHandler.delete

process/ -> ProcessHandler
GET -> ProcessHandler.get {data: [String, ...]}
GET name=<name> -> ProcessHandler.get {data: Object}

stream -> WebSocket
WS -> WebSocket.open
SEND -> WebSocket.on_message
RECV -> WebSocket.write_message
"""

configs = [
    {
        "name": "main-clock",
        "time": {
            "at": [ ],
            "after": [ ],
            "every": [ 1 ]
        },
        "data": [
            {
                "name": True,
                "args": [
                    { "key": "t_dt", "value": J2000 },
                    { "key": "dt_td", "value": SECOND }
                ]
            },
        ],
        "ctrl": [
            { "name": "ob.clock.clock", "args": [ None, True ] }
        ]
    },
    {
        "name": "test",
        "time": {
            "at": [ ],
            "after": [ ],
            "every": [ ]
        },
        "data": [
            {
                "name": "main-clock",
                "args": [ ]
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
            { "name": "ob.geo.sidereal", "args": [ "main-clock", "orb.iss" ] },
            { "name": "ob.orb.simple", "args": [ "main-clock", "orb.iss" ] },
            { "name": "ob.orb.rec2orb", "args": [ "earth", "orb.iss", "iss.apse", "iss.pole" ] },
            { "name": "ob.vec.fun2obl", "args": [ "iss.apse", "iss.pole", "orb.iss", "iss.pqw" ] },
            { "name": "ob.vec.rec2sph", "args": [ "iss.pqw" ] },
            { "name": "ob.vec.rec2sph", "args": [ "iss.apse" ] },
            { "name": "ob.vec.rec2sph", "args": [ "iss.pole" ] },
            { "name": "ob.orb.sph2kep", "args": [ "iss.pqw", "iss.apse", "iss.pole", "iss.kep" ] },
        ]
    }
]
message = dumps(configs)

class ObBaseHandler(tornado.web.RequestHandler):
    
    def initialize(self, ob):
        self._ = ob

class ObSystemHandler(ObBaseHandler):
        
    def get(self):
        try:
            name = self.get_query_argument("name")
            data = self._.System[name]._config
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            data = sorted([name for name in self._.System])
            status = httplib.OK
        except IndexError:
            data = None
            status = httplib.NOT_FOUND
        finally:
            self.add_header("Content-Type", "application/json")
            self.write(dumps({"data": data}))
            self.set_status(status)
        
    def post(self):
        try:
            data = loads(self.request.body)["data"]
            self._.start(data)
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        except IndexError:
            status = httplib.NOT_FOUND
        finally:
            self.set_status(status)
        
    def delete(self):
        try:
            self._.stop(self.get_query_argument("name"))
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        except IndexError:
            status = httplib.NOT_FOUND
        finally:
            self.set_status(status)

class ObProcessHandler(ObBaseHandler):
        
    def get(self):
        try:
            name = self.get_query_argument("name")
            data = self._.Process[name]._config._asdict()
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            data = sorted([name for name in self._.Process])
            status = httplib.OK
        except IndexError:
            data = None
            status = httplib.NOT_FOUND
        finally:
            self.add_header("Content-Type", "application/json")
            self.write(dumps({"data": data}))
            self.set_status(status)

class ObWebSocket(tornado.websocket.WebSocketHandler, ObBaseHandler):
    
    def open(self):
        for name in self._.System:
            self._.System[name].watch(self._on_data)
            self._.System[name].listen(self._on_ctrl)

    def on_close(self):
        for name in self._.System:
            self._.System[name].unwatch(self._on_data)
            self._.System[name].unlisten(self._on_ctrl)

    def on_message(self, message):
        packet = loads(message)
        
        name = packet["name"]
        if "data" in packet:
            packet["data"] = {d["key"]: d["value"]
                              for d in packet["data"]}
            self._.System[name].set(packet["data"])
        if "ctrl" in packet:
            self._.System[name].go(packet["ctrl"])

    def _on_data(self, name, packet):
        packet = [{"key": default(key), "value":packet[key]}
                  for key in packet]
        self.write_message(dumps({"name": name,
                                  "data": packet}))

    def _on_ctrl(self, name, packet):
        self.write_message(dumps({"name": name,
                                  "ctrl": packet}))

def main():
    loop = tornado.ioloop.IOLoop.current()
    env = TornadoEnvironment(loop, strict=False)
        
    configs = loads(message)

    ob = Ouroboros(env, loop)
    
    ob.start(configs[0])
    ob.start(configs[1])
    
    app = tornado.web.Application([(r"/ob-rest-api/system",
                                    ObSystemHandler, {"ob": ob}),
                                   (r"/ob-rest-api/process",
                                    ObProcessHandler, {"ob": ob}),
                                   (r"/ob-rest-api/stream",
                                    ObWebSocket, {"ob": ob}),
                                   (r'/(.*)', tornado.web.StaticFileHandler,
                                    {"path": os.path.join(os.path.dirname(__file__),
                                                          "static"),
                                     "default_filename": "index.html"})])
    app.listen(8000)
    
    loop.start()

if __name__ == '__main__':
    main()