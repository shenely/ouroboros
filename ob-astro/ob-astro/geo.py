# built-in libraries
import math
import datetime
import itertools

# external libraries
import numpy

# internal libraries
from ouroboros import Image, Node
from ouroboros.lib import libgeoid, libatmo

# exports
__all__ = ("jd", "st", "ax", "rose",
           # "igrf", "wmm", "egm",
           "sph2geo", "geo2sph")

# constants
JD_EPCOH = datetime.datetime(1858, 11, 16, 12)
RJD_OFFSET = 2400000
J2000_OFFSET = 2451545

O_BAR = numpy.array([0,0,0])
I_HAT = numpy.array([1,0,0])
J_HAT = numpy.array([0,1,0])
K_HAT = numpy.array([0,0,1])


def dms2deg(d=0.0, m=0.0, s=0.0):
    return d + (m + s / 60.0) / 60.0


##@Process("geo.model",
##         ([], ["tock"], {"sph": True}, ["az", "az_t"], []),
##         ([], [], [], [], ["_bar", "_t_bar"]))
##def model():
##    """Ground station"""
##    az, az_t, = yield
##
##    cos_az = cos(az)
##    sin_az = sin(az)
##
##    _hat = - sin_az * I + cos_az * J
##    _t_hat = - az_t * (cos_az * I + sin_az * J)
##    
##    print _hat, _t_hat
##
##    yield _hat, _t_hat


@Image("geo.jd",
       clk=Node(evs=(8601,), args=(),
                ins=(), reqs=("t_dt",),
                outs=(), pros=()),
       bod=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("jd",), pros=("jdn", "ut",
                                    "jd", "jc")))
def jd(clk, bod):
    """Julian date"""
    yield
    while True:
        t_dt, = clk.reqs
        
        s = (t_td - JD_EPOCH).total_seconds()
        rjd, ut = divmod(s / 3600, 24)
        jdn = rjd + RJD_OFFSET
        jd = jdn + ut / 24
        jc = (jdn - J2000_OFFSET) / 36525

        bod.pros = jdn, ut, jd, jc
        yield (bod.outs((True,)),)

@Image("geo.st",
       bod=Node(evs=(), args=(),
                ins=(), reqs=("jc", "ut"),
                outs=("gst",), pros=("gst",)),
       usr=Node(evs=("geo",), args=(),
                ins=(), reqs=("lon",),
                outs=("lst",), pros=("lst",)))
def st(bod, usr):
    """Sidereal time"""
    yield
    while True:
        jc, ut = bod.reqs
        
        gst0 = (100.4606184 +
                (36000.77004 +
                 (0.000387933 -
                  2.583e-8 * jc) * jc) * jc)
        gst = gst0 + 360.98564724 * ut / 24

        bod.pros = math.radians(gst % 360),
        usr.pros = math.radians((gst + lon) % 360),
        yield (bod.outs((True,)),
               usr.outs((True,)))


@Image("geo.axis",
       bod=Node(evs=("gst",), args=(),
                ins=(), reqs=("jc", "gst"),
                outs=("ax",), pros=("obl", "th_bar", "om_bar")))
def ax(bod):
    """Rotation axis"""
    yield
    while True:
        jc, gst = bod.reqs
        
        obl = (dms2deg(23, 26, 21.45) -
               (dms2deg(s=46.815) +
                (dms2deg(s=0.0059) -
                 dms2deg(s=0.00181) * jc) * jc) * jc)
        k_hat = (math.sin(obl) * I_HAT +
                 math.cos(obl) * K_HAT)
        th_bar = gst * k_hat
        om_bar = 360.98564724 / (24 * 60 * 60) * k_hat

        bod.pros = math.radians(obl % 360), th_bar, om_bar
        yield (bod.outs((True,)),)

@Image("geo.rose",
       usr=Node(evs=("geo",), args=(),
                ins=(), reqs=("lat", "lon"),
                outs=("rose",), pros=("E", "N", "Z")))
def rose(usr):
    """Compass rose"""
    yield
    while True:
        lat, lon = usr.reqs
        clon = math.cos(lon)
        slon = math.sin(lon)
        clat = math.cos(lat)
        slat = math.sin(lat)

        E = J_HAT * clon - I_HAT * slon
        N = (I_HAT * clon + J_HAT * slon) * slat + K_HAT * clat
        Z = (I_HAT * clon + J_HAT * slon) * clat + K_HAT * slat


        usr.pros = E, N, Z
        yield usr.outs((True,))


@Image("geo.std_atmo",
       sun=Node(evs=(), args=(),
                ins=(), reqs=("f10p7",),
                outs=(), pros=()),
       geo=Node(evs=(), args=("R",),
                ins=(), reqs=(),
                outs=(), pros=()),
       usr=Node(evs=(False,), args=(),
                ins=(), reqs=("alt",),
                outs=(True,), pros=("rho", "p", "T")))
def std_atmo(sun, geo, usr):
    """Standard atmosphere"""
    R, = geo.args
    
    yield
    while True:
        z, = atmo.reqs
        f10p7, = sun.reqs
        h = R * z / (R + z)
        usr.pros = libatmo.std_atmo(h, f10p7)
        yield (usr.outs((True,)),)
        

@Image("geo.sph2geo",
       bod=Node(evs=(), args=("R", "f"),
                ins=(), reqs=(),
                outs=(), pros=()),
       sph=Node(evs=(), args=(),
                ins=("sph",), reqs=("lat", "lon", "rad"),
                outs=(), pros=()),
       geo=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("geo",), pros=("lat", "lon", "alt")))
def sph2geo(bod, sph, geo):
    """Geocentric to geodetic coordinates"""
    R, f = bod.args
    
    yield
    while True:
        libgeoid.setshape(R, f)

        lat_c, lon_c, rad_c = sph.reqs
        lat_d, lon_d, alt_d = libgeoid.center2datum(lat_c, lon_c, rad_c)
        geo.pros = lat_d, lon_d, alt_d
        yield (geo.outs((True,)),)


@Image("geo.geo2sph",
       bod=Node(evs=(), args=("R", "f"),
        ins=(), reqs=(),
        outs=(), pros=()),
       sph=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("sph",), pros=("lat", "lon", "rad")),
       geo=Node(evs=("geo",), args=(),
                ins=(), reqs=("lat", "lon", "alt"),
                outs=(), pros=()))
def geo2sph(bod, sph, geo):
    """Geodetic to geocentric coordinates"""
    R, f = bod.args
    
    yield
    while True:
        libgeoid.setshape(R, f)

        lat_d, lon_d, alt_d = geo.reqs
        lat_c, lon_c, rad_c = libgeoid.datum2center(lat_d, lon_d, alt_d)
        sph.pros = lat_c, lon_c, rad_c
        yield (sph.outs((True,)),)
