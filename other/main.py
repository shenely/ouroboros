from math import sqrt, radians
from datetime import datetime, timedelta

from numpy import array

from core import System
from clock import *
from orbit import *
from geo import *
from vector import *
import web

EARTH_RADIUS = 6378.1370
EARTH_FLATTENING = 1 / 298.257223563
EARTH_GRAVITATION = 398600.4418

J2000 = datetime(2000,1,1,12)#Julian epoch (2000-01-01T12:00:00Z)

SECOND = timedelta(seconds=1)
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

#Unit vectors
O = array([0,0,0])
I = array([1,0,0])
J = array([0,1,0])
K = array([0,0,1])

def main():
    web.main()

    sys = System(t_dt=datetime.utcnow(),
                 dt_td=SECOND)

    sys.init("earth",
             mu=EARTH_GRAVITATION,
             f=EARTH_FLATTENING,
             R_km=EARTH_RADIUS)
    sys.init(("geo", "mtv"),
             r=0.032, r_t=0,
             az=radians(-122-(4.0-55.0/60)/60), az_t=0,
             el=radians(37+(23.0+22.0/60)/60), el_t=0)
    sys.init(("orb", "iss"),
             line1="1 25544U 98067A   16038.90574315  .00010255  00000-0  15975-3 0  9995",
             line2="2 25544  51.6448 347.7333 0006934  92.9813   9.9319 15.54494719984713")

    sys.at(0)
    sys.every(1, until=3600)

    clock(sys, None)
    sidereal(sys, None, ("earth", "axis"))
    
    ground(sys, None, ("geo", "mtv"), ("mtv", "east"))
    sph2rec(sys, ("geo", "mtv"))
    geo2rec(sys, "earth", ("geo", "mtv"), ("earth", "mtv"))

    orbit(sys, None, ("orb", "iss"))
    nrt2rot(sys, ("earth", "axis"), ("orb", "iss"), ("earth", "iss"))
    
    abs2rel(sys, ("earth", "mtv"), ("earth", "iss"), ("gnd", "iss"))
    fun2obl(sys, ("mtv", "east"), ("geo", "mtv"), ("gnd", "iss"), ("mtv", "iss"))
    rec2sph(sys, ("mtv", "iss"))

    sys.run()
    
if __name__ == "__main__":
    main()