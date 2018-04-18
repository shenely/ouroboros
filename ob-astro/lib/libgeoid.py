#built-in libraries
import os.path
import ctypes
import logging

#external libraries
import numpy
import numpy.ctypeslib

#internal libraries
path = os.path.dirname(__file__)
libgeoid = numpy.ctypeslib.load_library('_libgeoid', path)

#exports
__all__ = ('settol', 'setiter',
           'setshape',
           'center2datum',
           'datum2center')

#constants
MINUTE = 60.0#seconds

#types
c_double_p = ctypes.POINTER(ctypes.c_double)

#int settol(double)
libgeoid.settol.argtypes = [ctypes.c_double]
libgeoid.settol.restype = ctypes.c_int
def settol(tol):
    if libgeoid.settol(tol) != 0:
        raise

#int setmaxiter(int)
libgeoid.setmaxiter.argtypes = [ctypes.c_int]
libgeoid.setmaxiter.restype = ctypes.c_int
def setmaxiter(maxiter):
    if libgeoid.setmaxiter(maxiter) != 0:
        raise

#int setshape(double, double)
libgeoid.setshape.argtypes = [ctypes.c_double,
                              ctypes.c_double]
libgeoid.setshape.restype = ctypes.c_int
def setshape(R, f):
    if libgeoid.setshape(R, f) != 0:
        raise

#int center2datum(double, double, double*, double*)
libgeoid.center2datum.argtypes = [ctypes.c_double,
                                  ctypes.c_double,
                                  c_double_p, c_double_p]
libgeoid.center2datum.restype = ctypes.c_int
def center2datum(lat_c, lon, rad_c):
    lat_d = ctypes.c_double()
    alt_d = ctypes.c_double()
    if libgeoid.center2datum(lat_c, rad_c,
                             ctypes.byref(lat_d),
                             ctypes.byref(alt_d)) != 0:
        raise
    return (lat_d.value, lon, alt_d.value)

#int datum2center(double, double, double*, double*)
libgeoid.datum2center.argtypes = [ctypes.c_double,
                                  ctypes.c_double,
                                  c_double_p, c_double_p]
libgeoid.datum2center.restype = ctypes.c_int
def datum2center(lat_d, lon, alt_d):
    lat_c = ctypes.c_double()
    rad_c = ctypes.c_double()
    if libgeoid.datum2center(lat_d, alt_d,
                             ctypes.byref(lat_c),
                             ctypes.byref(rad_c)) != 0:
        raise
    return (lat_c.value, lon, rad_c.value)

def main():pass
    
if __name__ == '__main__':
    main()
