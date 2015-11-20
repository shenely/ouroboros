from math import sqrt
from datetime import datetime,timedelta

from numpy import array, matrix

from .core import System
from .orbit import *

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
I = array([1,0,0])
J = array([0,1,0])
K = array([0,0,1])

def main():
    sys = System(t_dt=J2000,
                 dt_td=SECOND)
    sys.set("earth",
            th_G=100.4606184,
            mu=EARTH_GRAVITATION,
            f=EARTH_FLATTENING,
            R_km=EARTH_RADIUS)
    sys.set("gs",lat_deg=60,lon_deg=-60,alt_m=100)
    sys.set("sc",r_bar=7000.0*I,v_bar=7.0*J)
    
    sys.every(1,until=3600)
    sys.every(10,until=3600)
    sys.every(60,until=3600)
    
    clock(sys,None)
    earth(sys,None,"earth")
    geo(sys,None,"gs","earth")
    orbit(sys,None,"sc","earth")
    
    sys._env.run()
    
if __name__ == "__main__":
    main()