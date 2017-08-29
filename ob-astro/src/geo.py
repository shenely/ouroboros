#built-in libraries
from math import sqrt, radians, cos, sin

#external libraries
import numpy

#internal libraries
from ouroboros import NORMAL, Item, coroutine, PROCESS

#exports
__all__ = ('jd', 'st',
           'axis', 'rose', 'fixed',
           'sph2geo', 'geo2sph')

#constants

#constants
O_BAR = numpy.array([0,0,0])
I_HAT = numpy.array([1,0,0])
J_HAT = numpy.array([0,1,0])
K_HAT = numpy.array([0,0,1])

def dms2deg(d=0.0, m=0.0, s=0.0):
    return d + (m + s / 60.0) / 60.0

@coroutine
def cardinal():
    lat, lon = yield
    while True:
        clon = cos(lon)
        slon = sin(lon)
        clat = cos(lat)
        slat = sin(lat)
        
        north = ((I_HAT * clon +
                   J_HAT * slon) * slat +
                 K_HAT * clat)
        south = - north
        east = (J_HAT * clon -
                I_HAT * slon)
        west = - east
        zenith = ((I_HAT * clon +
                   J_HAT * slon) * clat +
                  K_HAT * slat)
        nadir = - zenith
        lat, lon = yield (north, south,
                          east, west,
                          zenith, nadir)

@coroutine
def geoc2d(rad_e, f):
    e__2 = (2 - f) * f
    fn1__2 = (1 - f) * (1 - f)
    
    lat_d, lon_d, alt_d = yield
    while True:
        lat_d = lat_c
        lon_d = lon_c
        alt_c = rad_c - rad_e
        cos_c = cos(lat_c)
        sin_c = sin(lat_c)
        for i in xrange(maxiter):
            cos_d = cos(lat_d)
            sin_d = sin(lat_d)
            d = 1 - e__2 * sin_d * sin_d
            rad_d = rad_e / sqrt(d)
            
            g = (rad_d + alt_d) * cos_d - rad_c * cos_c
            h = (rad_d * fn1__2 + alt_d) * sin_d - rad_c * sin_c
            g_lat = - (rad_d * fn1__2 / d + alt_d) * sin_d
            g_alt = cos_d
            h_lat = (rad_d * fn1__2 / d + alt_d) * cos_d
            h_alt = sin_d
            
            det = g_lat * h_alt - g_alt * h_lat
            delta_lat = (g * h_alt - h * g_lat) / det
            delta_alt = (h * g_lat - g * h_alt) / det
            if abs(delta_lat) < tol and abs(delta_alt) < tol:break
            else:
                lat_d -= delta_lat
                alt_d -= delta_alt
        else:pass#warning
        lat_c, lon_c, rad_c = yield lat_d, lon_d, alt_d

@coroutine
def geod2c(rad_e, f):
    e__2 = (2 - f) * f
    fn1__2 = (1 - f) * (1 - f)
    
    lat_d, lon_d, alt_d = yield
    while True:
        cos_d = cos(lat_d)
        sin_c = sin(lat_d)
        sqrt_d = sqrt(1 - e__2 * sin_d * sin_d)
        
        rad_cos_lat = (rad_e / sqrt_d + alt_d) * cos_d
        rad_sin_lat = (rad_e * fn1__2 / sqrt_d + alt_d) * sin_d

        lat_c = atan2(rad_sin_lat, rad_cos_lat)
        lon_c = lon_d
        rad_c = sqrt(rad_sin_lat * rad_sin_lat +
                     rad_cos_lat * rad_cos_lat)
        lat_d, lon_d, alt_d = yield lat_c, lon_c, rad_c

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
              ins=(8601,), reqs=('t_dt',),
              outs=(), pros=()),
         Item('bod',
              evs=(), args=(),
              ins=('jd',), reqs=(),
              outs=('jd',), pros=('jdn', 'ut',
                                  'jd', 'jc')))
def jd(clk, bod):
    """Julian date"""
    right = yield
    while True:
        clk, bod = (right['clk'],
                    right['bod'])
        
        (t_dt,), (iso_e,) = clk.next()
        _, (jd_e,) = bod.next()
        if iso_e and not jd_e:
            jdn = (367 * t_dt.year -
                   (7 * (t_dt.year + (t_dt.month + 9) / 12) / 4) +
                   275 * t_dt.month / 9 +
                   t_dt.day + 1721013.5)
            ut = (t_dt.hour +
                  (t_dt.minute +
                   (t_dt.second +
                    t_dt.microsecond
                    / 1e6)
                   / 60)
                  / 60)
            jd = jdn + ut / 24
            jc = (jdn - 2451545) / 36525
            bod = ((jdn, ut, jd, jc), (True,)),
        else:bod = None

        left = ({'bod': bod}
                if bod is not None
                else {})
        right = yield left

@PROCESS('geo.st', NORMAL,
         Item('bod',
              evs=('jd',), args=(),
              ins=('jd', 'gst'), reqs=('jc', 'ut'),
              outs=('gst',), pros=('gst', 'gst_t')),
         Item('usr',
              evs=('geo',), args=(),
              ins=('geo', 'lst'), reqs=('lon,'),
              outs=('lst',), pros=('lst',)))
def st(bod, usr):
    """Sidereal time"""
    right = yield
    while True:
        bod, usr = (right['bod'],
                    right['usr'])
        
        (jc, ut), (jd_e, gst_e) = bod.next()
        if jd_e and not gst_e:
            gst0 = (100.4606184 +
                    (36000.77004 +
                     (0.000387933 -
                      2.583e-8 * jc) * jc) * jc)
            gst = gst0 + 360.98564724 * ut / 24
            gst_t = 360.98564724 / (24 * 60 * 60)
            bod = ((radians(gst % 360),), (True,)),
            usr = ((((radians((gst + lon) % 360),
                      radians(gst_t)), (True,))
                    if geo_e and not lst_e else
                    ((None,), (False,)))
                   for (lon,), (geo_e, lst_e) in usr)
        else:bod = usr = None

        left = ({'bod': bod,
                 'usr': usr}
                if bod is not None
                else {})
        right = yield left

@PROCESS('geo.axis', NORMAL,
         Item('bod',
              evs=('jd',), args=(),
              ins=('jd',), reqs=('jc', 'gst', 'gst_t'),
              outs=(), pros=('obl',)),
         Item('usr',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('th_bar', 'om_bar')))
def axis(bod, usr):
    """Rotation axis"""
    right = yield
    while True:
        bod, usr = (right['bod'],
                    right['usr'])
        
        (jc,), (jd_e,) = bod.next()
        _, (rec_e,) = usr.next()
        if jd_e and not rec_e:
            obl = (dms2deg(23, 26, 21.45) -
                   (dms2deg(s=46.815) +
                    (dms2deg(s=0.0059) -
                     dms2deg(s=0.00181) * jc) * jc) * jc)
            k_hat = (sin(obl) * I_HAT +
                     cos(obl) * K_HAT)
            th_bar = gst * k_hat
            om_bar = gst_t * k_hat
            bod = ((radians(obl % 360),), (True,)),
            usr = ((th_bar, om_bar), (True,)),
        else:bod = usr = None

        left = ({'bod': bod,
                 'usr': usr}
                if bod is not None
                else {})
        right = yield left

@PROCESS('geo.rose', NORMAL,
         Item('usr',
              evs=('geo',), args=(),
              ins=('geo', 'rose'), reqs=('lat', 'lon'),
              outs=('rose',), pros=('north', 'south',
                                    'east', 'west',
                                    'zenith', 'nadir')))
def rose(usr):
    """Compass rose"""
    compass = cardinal()
    
    right = yield
    while True:
        usr = right['usr']
        usr = (((compass.send((lat, lon)), (True,))
                if geo_e and not rose_e else
                ((None, None,
                  None, None,
                  None, None), (False,)))
               for (lat, lon), (geo_e, rose_e) in usr)

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
              ins=('geo',), reqs=(),
              outs=('geo',), pros=('lat', 'lon', 'alt')))
def sph2geo(bod, sph, geo):
    """Geocentric to geodetic coordinates"""
    R, f = bod.next()
    datum = geoc2d(R, f)
    
    right = yield
    while True:
        bod, sph, geo = (right['bod'],
                         right['sph'],
                         right['geo'])
        
        geo = (((datum.send((lat_c, lon_c, rad_c)), (True,))
                if sph_e and not geo_e else
                ((None, None, None), (False,)))
               for (((lat_c, lon_c, rad_c), (sph_e,)),
                    (_, (geo_e,))) in zip(sph, geo))

        left = {'geo': geo}
        right = yield left

@PROCESS('geo.geo2sph', NORMAL,
         Item('bod',
              evs=(), args=('R', 'f'),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sph',
              evs=(), args=('lat', 'lon', 'rad'),
              ins=('sph',), reqs=(),
              outs=('sph',), pros=()),
         Item('geo',
              evs=('geo',), args=(),
              ins=('geo',), reqs=('lat', 'lon', 'alt'),
              outs=(), pros=()))
def geo2sph(bod, sph, geo):
    """Geodetic to geocentric coordinates"""
    R, f = bod.next()
    center = geod2c(R, f)
    
    right = yield
    while True:
        bod, sph, geo = (right['bod'],
                         right['sph'],
                         right['geo'])
        
        sph = (((center.send((lat_d, lon_d, alt_d)), (True,))
                if geo_e and not sph_e else
                ((None, None, None), (False,)))
               for (((lat_d, lon_d, alt_d), (geo_e,)),
                    (_, (sph_e,))) in zip(geo, sph))

        left = {'sph': sph}
        right = yield left
