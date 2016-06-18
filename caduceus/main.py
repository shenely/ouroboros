import math
import datetime
import threading

import numpy
import simpy
import tornado.ioloop

from core import System
from util import dumps, loads
import clock, vec, geo, orb, web

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

configs = [
    {
        "name": "test",
        "time": {
            "at": [ 0 ],
            "after": [ ],
            "every": [ 1 ]
        },
        "data": [
            {
                "name": None,
                "args": [
                    { "key": "t_dt", "value": datetime.datetime.utcnow() },
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
                    { "key": "line1", "value": "1 25544U 98067A   16160.86541705 -.00081986  00000-0 -12286-2 0  9995" },
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
    }
]
message = dumps(configs)

class Service(object):
    
    def __init__(self, config):
        self._env = simpy.RealtimeEnvironment()
    
        [System(self._env, config)
         for config in loads(message)]
    
        self._loop = tornado.ioloop.IOLoop.current()
    
    def watch(self, name, callback):
        System[name].watch(callback)
    
    def listen(self, name, callback):
        System[name].listen(callback)
        
    def wave(self, name, values):
        System[name].set(values)
        
    def yell(self, name, keys):
        System[name].go(keys)
    
    def run(self):
        def caller():
            self._env.step()
            self._loop.add_callback(caller)
        
        self._loop.add_callback(caller)
        self._loop.start()

def test():print "test"

def main():
    #web.main()
    
    env = simpy.RealtimeEnvironment()
    
    [System(env, config)
     for config in loads(message)]
    
    loop = tornado.ioloop.IOLoop.current()
        
    loop.add_callback(env.run)
    loop.call_later(5, test)
    loop.start()
    
if __name__ == "__main__":
    main()