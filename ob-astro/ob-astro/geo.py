#built-in libraries
import math
import datetime
import logging

#external libraries
import numpy

#internal libraries
from ouroboros import NORMAL, Item, coroutine, PROCESS
from ouroboros.lib import libgeoid

#exports
__all__ = ('jd', 'st', 'ax', 'rose',
           #'igrf', 'wmm', 'egm',
           'sph2geo', 'geo2sph')

#constants
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

@PROCESS('geo.jd', NORMAL,
         Item('clk',
              evs=(8601,), args=(),
              ins=(), reqs=('t_dt',),
              outs=(), pros=()),
         Item('bod',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('jd',), pros=('jdn', 'ut',
                                  'jd', 'jc')))
def jd(clk, bod):
    """Julian date"""
    right = yield
    while True:
        clk = right['clk']

        (t_dt,), _ = clk.next()
        s = (t_td - JD_EPOCH).total_seconds()
        rjd, ut = divmod(s / 3600, 24)
        jdn = rjd + RJD_OFFSET
        jd = jdn + ut / 24
        jc = (jdn - J2000_OFFSET) / 36525
        bod = ((jdn, ut, jd, jc), (True,)),

        left = {'bod': bod}
        right = yield left

@PROCESS('geo.st', NORMAL,
         Item('bod',
              evs=(), args=(),
              ins=(), reqs=('jc', 'ut'),
              outs=('gst',), pros=('gst',)),
         Item('usr',
              evs=('geo',), args=(),
              ins=('geo',), reqs=('lon',),
              outs=('lst',), pros=('lst',)))
def st(bod, usr):
    """Sidereal time"""
    right = yield
    while True:
        bod, usr = (right['bod'],
                    right['usr'])
        
        (jc, ut), _ = bod.next()
        gst0 = (100.4606184 +
                (36000.77004 +
                 (0.000387933 -
                  2.583e-8 * jc) * jc) * jc)
        gst = gst0 + 360.98564724 * ut / 24
        bod = (((radians(gst % 360),), (True,)),)
        usr = ((((radians((gst + lon) % 360),), (True,))
                if geo_e else ((None,), (None,)))
               for (lon,), (geo_e,) in usr)

        left = {'bod': bod,
                'usr': usr}
        right = yield left

@PROCESS('geo.axis', NORMAL,
         Item('bod',
              evs=('gst',), args=(),
              ins=(), reqs=('jc', 'gst'),
              outs=('ax',), pros=('obl', 'th_bar', 'om_bar')))
def ax(bod):
    """Rotation axis"""
    right = yield
    while True:
        bod = right['bod']
        
        (jc, gst), _ = bod.next()
        obl = (dms2deg(23, 26, 21.45) -
               (dms2deg(s=46.815) +
                (dms2deg(s=0.0059) -
                 dms2deg(s=0.00181) * jc) * jc) * jc)
        k_hat = (sin(obl) * I_HAT +
                 cos(obl) * K_HAT)
        th_bar = gst * k_hat
        om_bar = 360.98564724 / (24 * 60 * 60) * k_hat
        bod = (((radians(obl % 360), th_bar, om_bar), (True,)),)

        left = {'bod': bod}
        right = yield left

@PROCESS('geo.rose', NORMAL,
         Item('usr',
              evs=('geo',), args=(),
              ins=('geo',), reqs=('lat', 'lon'),
              outs=('rose',), pros=('east', 'north', 'zenith')))
def rose(usr):
    """Compass rose"""
    right = yield
    while True:
        usr = right['usr']
        usr = (((cos(lon), sin(lon),
                 cos(lat), sin(lat)), _)
                 for (lat, lon), _ in usr)
        usr = ((((J_HAT * clon - I_HAT * slon,
                  I_HAT * clon + J_HAT * slon) * slat + K_HAT * clat,
                 (I_HAT * clon + J_HAT * slon) * clat + K_HAT * slat), _)
               for (clon, slon, clat, slat), _ in usr)
        usr = (((E, N, Z), (True,))
               if geo_e else ((None,) * 3, (None,))
               for (E, N, Z), (geo_e,) in usr)

        left = {'usr': usr}
        right = yield left

@PROCESS('geo.sph2geo', NORMAL,
         Item('bod',
              evs=(), args=('R', 'f'),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sph',
              evs=('sph',), args=(),
              ins=('sph',), reqs=('lat', 'lon', 'rad'),
              outs=(), pros=()),
         Item('geo',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('geo',), pros=('lat', 'lon', 'alt')))
def sph2geo(bod, sph, geo):
    """Geocentric to geodetic coordinates"""
    R, f = bod.next()
    
    right = yield
    while True:
        sph, = right['sph']
        
        libgeoid.setshape(R, f)
        geo = (((libgeoid.center2datum
                 (lat_c, lon_c, rad_c), (True,))
                if sph_e
                else (None, None))
               for ((lat_c, lon_c, rad_c), (sph_e,)) in sph)

        left = {'geo': geo}
        right = yield left

@PROCESS('geo.geo2sph', NORMAL,
         Item('bod',
              evs=(), args=('R', 'f'),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sph',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('sph',), pros=('lat', 'lon', 'rad')),
         Item('geo',
              evs=('geo',), args=(),
              ins=('geo',), reqs=('lat', 'lon', 'alt'),
              outs=(), pros=()))
def geo2sph(bod, sph, geo):
    """Geodetic to geocentric coordinates"""
    R, f = bod.next()
    
    right = yield
    while True:
        geo = right['geo']
        
        libgeoid.setshape(R, f)
        sph = (((libgeoid.datum2center
                 (lat_d, lon_d, alt_d), (True,))
                if geo_e else
                 (None, None))
               for ((lat_d, lon_d, alt_d), (geo_e,)) in geo)

        left = {'sph': sph}
        right = yield left
