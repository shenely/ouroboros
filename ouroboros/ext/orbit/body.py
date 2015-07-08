#!/usr/bin/env python2.7

"""Celestial bodies

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   07 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from math import sqrt

#External libraries
from sgp4.earth_gravity import *

#Internal libraries
from ouroboros.behavior import behavior,PrimitiveBehavior
#
##################=


##################
# Export section #
#
__all__ = ["CelestialPrimitive",
           "StarPrimitive",
           "Sun",
           "PlanetPrimitive",
           "Earth",
           "EarthOld",
           "EarthWGS72",
           "EarthWGS84",
           "MoonPrimitive",
           "Moon"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################

@behavior(name="CelestialPrimitive",
          type="PrimitiveBehavior",
          nodes=[{"name":"R",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"mu",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"J2",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"J3",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"J4",
                  "type":"NumberPrimitive","args":[]}])
class CelestialPrimitive(PrimitiveBehavior):
    
    def _update(self,*args,**kwargs):
        super(CelestialPrimitive,self)._update(*args,**kwargs)
        
        radiusearthkm = kwargs.get("R")
        mu = kwargs.get("mu")
        j2 = kwargs.get("J2",0)
        j3 = kwargs.get("J3",0)
        j4 = kwargs.get("J4",0)
        
        assert radiusearthkm is not None
        assert mu is not None
        
        xke    = 60.0 / sqrt(radiusearthkm*radiusearthkm*radiusearthkm/mu);
        tumin  = 1.0 / xke;
        j3oj2  =  j3 / j2 if j2 != 0 and j3 != 0 else 1
        
        self.gravity = EarthGravity(tumin,mu,radiusearthkm,xke,j2,j3,j4,j3oj2)

@behavior(name="StarPrimitive",
          type="CelestialPrimitive",
          nodes=[{"name":"R",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"mu",
                  "type":"NumberPrimitive","args":[]}])
class StarPrimitive(CelestialPrimitive):pass

@behavior(name="Sun",
          type="StarPrimitive")
class Sun(StarPrimitive):
    
    def _update(self,*args,**kwargs):
        kwargs["R"] = 696342.0
        kwargs["mu"] = 132712440018.0
        
        kwargs["mu"] = 132712440018.0
        
        super(Sun,self)._update(*args,**kwargs)

@behavior(name="PlanetPrimitive",
          type="CelestialPrimitive",
          nodes=[{"name":"R",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"mu",
                  "type":"NumberPrimitive","args":[]}])
class PlanetPrimitive(CelestialPrimitive):pass

@behavior(name="Earth",
          type="PlanetPrimitive")
class Earth(PlanetPrimitive):
    
    def _update(self,*args,**kwargs):
        kwargs["R"] = 6378.1
        kwargs["mu"] = 398600.4418
        
        super(Earth,self)._update(*args,**kwargs)

@behavior(name="EarthOld",
          type="Earth")
class EarthOld(Earth):
    
    def _update(self,*args,**kwargs):
        kwargs.update(wgs72old._asdict())
        
        super(Earth,self)._update(*args,**kwargs)

@behavior(name="EarthWGS72",
          type="Earth")
class EarthWGS72(Earth):
    
    def _update(self,*args,**kwargs):
        kwargs.update(wgs72._asdict())
        
        super(Earth,self)._update(*args,**kwargs)

@behavior(name="EarthWGS84",
          type="Earth")
class EarthWGS84(Earth):
    
    def _update(self,*args,**kwargs):
        kwargs.update(wgs84._asdict())
        
        super(Earth,self)._update(*args,**kwargs)

@behavior(name="MoonPrimitive",
          type="CelestialPrimitive",
          nodes=[{"name":"R",
                  "type":"NumberPrimitive","args":[]},
                 {"name":"mu",
                  "type":"NumberPrimitive","args":[]}])
class MoonPrimitive(CelestialPrimitive):pass

@behavior(name="Moon",
          type="MoonPrimitive")
class Moon(MoonPrimitive):
    
    def _update(self,*args,**kwargs):
        kwargs["R"] = 1738.14
        kwargs["mu"] = 4902.8000
        
        super(Earth,self)._update(*args,**kwargs)
        
def install(service):
    CelestialPrimitive.install(service)
    StarPrimitive.install(service)
    Sun.install(service)
    PlanetPrimitive.install(service)
    Earth.install(service)
    EarthOld.install(service)
    EarthWGS72.install(service)
    EarthWGS84.install(service)
    MoonPrimitive.install(service)
    Moon.install(service)