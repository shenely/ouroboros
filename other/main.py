from math import sqrt, radians
from datetime import datetime,timedelta

from numpy import array

from core import System
from clock import *
from orbit import *
from geo import *
from vector import *
import web

EARTH_RADIUS = 6378.1
EARTH_FLATTENING = 0.00335
EARTH_GRAVITATION = 398600.4

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

    sys = System(t_dt=J2000,
                 dt_td=MINUTE)

    sys.init("earth",
             mu=EARTH_GRAVITATION,
             f=EARTH_FLATTENING,
             R_km=EARTH_RADIUS)
    sys.init(("gs", "geo"),
             r=0.1, r_t=0,
             az=radians(45), az_t=0,
             el=radians(45), el_t=0)
    sys.init(("gs", "e"),
             _bar=sqrt(2)*(J-I)/2,
             _t_bar=O)
    sys.init(("sc", "orb"), _bar=sqrt(2)*7000.0*(I+K)/2, _t_bar=7.5*J)

    sys.at(0)
    sys.every(1, until=3600)

    clock(sys, None)
    sidereal(sys, None, ("earth", "axis"))
    
    ground(sys, None, ("gs", "geo"))
    sph2rec(sys, ("gs", "geo"))
    geo2rec(sys, "earth", ("gs", "geo"), ("earth", "gs"))

    orbit(sys, None, ("sc", "orb"), "earth")
    nrt2rot(sys, ("earth", "axis"), ("sc", "orb"), ("earth", "sc", "orb"))
    
    abs2rel(sys, ("earth", "gs"), ("earth", "sc", "orb"), ("gs", "sc"))
    fun2obl(sys, ("gs", "e"), ("gs", "geo"), ("gs", "sc"), ("gs", "sc", "obs"))
    rec2sph(sys, ("gs", "sc", "obs"))

    sys.run()
    
if __name__ == "__main__":
    main()