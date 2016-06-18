from math import sqrt, radians
from datetime import datetime, timedelta

from numpy import array

from core import System
import clock, vec, geo, orb, web

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
             line1="1 25544U 98067A   16079.67549635  .00009878  00000-0  15582-3 0  9994",
             line2="2 25544  51.6436 144.4524 0001845 329.9530 167.3838 15.54205650991053")
    sys.init(("iss", "apse"), _t_bar=O)
    sys.init(("iss", "pole"), _t_bar=O)

    sys.at(0)
    sys.every(1, until=3600)

    clock.clock(sys, None)
    geo.sidereal(sys, None, ("earth", "axis"))

    orb.simple(sys, None, ("orb", "iss"))

    orb.rec2orb(sys, "earth", ("orb", "iss"), ("iss", "apse"), ("iss", "pole"))
    vec.fun2obl(sys, ("iss", "apse"), ("iss", "pole"), ("orb", "iss"), ("iss", "pqw"))

    vec.rec2sph(sys, ("iss", "pqw"))
    vec.rec2sph(sys, ("iss", "apse"))
    vec.rec2sph(sys, ("iss", "pole"))

    orb.sph2kep(sys, ("iss", "pqw"), ("iss", "apse"), ("iss", "pole"), ("iss", "kep"))

    sys.run()
    
if __name__ == "__main__":
    main()