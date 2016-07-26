import math
import time
import httplib
import datetime
import logging

import numpy
import simpy
import simpy.core
import tornado.web
import tornado.websocket
import tornado.ioloop

from caduceus import Caduceus, TornadoEnvironment
from util import loads, dumps, default

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
GET /caduceus.py -> CaduceusHandler.get
GET /caduceus.py?name=<name> -> CaduceusHandler.get
POST /caduceus.py (config) -> CaduceusHandler.post
DELETE /caduceus.py?name=<name> -> CaduceusHandler.delete
WS /caduceus.py/<name> -> CaduceusWebSocket.open
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
            { "name": "clock.clock", "args": [ None, True ] }
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
            { "name": "geo.sidereal", "args": [ "main-clock", "orb.iss" ] },
            { "name": "orb.simple", "args": [ "main-clock", "orb.iss" ] },
            { "name": "orb.rec2orb", "args": [ "earth", "orb.iss", "iss.apse", "iss.pole" ] },
            { "name": "vec.fun2obl", "args": [ "iss.apse", "iss.pole", "orb.iss", "iss.pqw" ] },
            { "name": "vec.rec2sph", "args": [ "iss.pqw" ] },
            { "name": "vec.rec2sph", "args": [ "iss.apse" ] },
            { "name": "vec.rec2sph", "args": [ "iss.pole" ] },
            { "name": "orb.sph2kep", "args": [ "iss.pqw", "iss.apse", "iss.pole", "iss.kep" ] },
        ]
    },
    {
        "name": "in-clock",
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
            { "name": "clock.clock", "args": [ None, True ] }
        ]
    },
    {
        "name": "out-clock",
        "time": {
            "at": [ ],
            "after": [ ],
            "every": [ ]
        },
        "data": [
            {
                "name": "in-clock",
                "args": [
                    { "key": "t_dt", "value": J2000 },
                    { "key": "dt_td", "value": HOUR }
                ]
            },
        ],
        "ctrl": [ ]
    }
]
message = dumps(configs)

class CaduceusHandler(tornado.web.RequestHandler):
    
    def initialize(self, _):
        self._ = _
        
    def get(self):
        try:
            name = self.get_query_argument("name")
            result = self._.System[name]._config
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            result = {"system": sorted([name for name in self._.System]),
                      "process": sorted([name for name in self._.Process])}
            status = httplib.OK
        except IndexError:
            result = None
            status = httplib.NOT_FOUND
        finally:
            self.write(dumps({"result": result}))
            self.set_status(status)
        
    def post(self):
        try:
            self._.start(loads(self.get_body_argument("config")))
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

class CaduceusWebSocket(tornado.websocket.WebSocketHandler):
    
    def initialize(self, _):
        self._ = _
    
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

    _ = Caduceus(env, loop)
    
    _.start(configs[0])
    _.start(configs[1])
    _.start(configs[2])
    _.start(configs[3])
    
    app = tornado.web.Application([(r"/caduceus.py", CaduceusHandler, {"_": _}),
                                   (r"/caduceus-stream", CaduceusWebSocket, {"_": _}),
                                   (r'/(.*)', tornado.web.StaticFileHandler,
                                    {"path": "static",
                                     "default_filename": "index.html"})])
    app.listen(8000)
    
    loop.start()

if __name__ == '__main__':
    main()