#built-in libraries
import os.path
import ctypes
import logging

#external libraries
import numpy
import numpy.ctypeslib

#internal libraries
path = os.path.dirname(__file__)
liborbele = numpy.ctypeslib.load_library('_liborbele', path)

#exports
__all__ = ('setmu',
           'inv2law',
           'rec2kep', 'kep2rec')

#types
c_double_p = ctypes.POINTER(ctypes.c_double)
np_vector3 = numpy.ctypeslib.ndpointer(dtype=numpy.float64,
                                      ndim=1, shape=(3,),
                                      flags='C')

class ob_orbele(ctypes.Structure):
    _fields_ = [('sma',  ctypes.c_double),
                ('mm',   ctypes.c_double),
                ('ecc',  ctypes.c_double),
                ('aop',  ctypes.c_double),
                ('raan', ctypes.c_double),
                ('inc',  ctypes.c_double),
                ('ta',   ctypes.c_double),
                ('ea',   ctypes.c_double),
                ('ma',   ctypes.c_double)]
ob_orbele_p = ctypes.POINTER(ob_orbele)

#int setmu(double)
liborbele.setmu.argtypes = [ctypes.c_double]
liborbele.setmu.restype = ctypes.c_int
def setmu(mu):
    if libunikep.setmu(mu) != 0:
        raise

#int inv2law(double*, double*, double*, double*, double*)
liborbele.inv2law.argtypes = [np_vector3, np_vector3,
                              c_double_p, np_vector3, np_vector3]
liborbele.setmu.restype = ctypes.c_int
def inv2law(r_bar, v_bar):
    eps = ctypes.c_double(),
    h_bar = numpy.empty_like(r_bar)
    e_bar = numpy.empty_like(r_bar)
    if liborbele.inv2law(r_bar, v_bar,
                         ctypes.byref(eps),
                         h_bar, e_bar) != 0:
        raise
    return (eps.value, h_bar, e_bar)

#int rec2kep(double*, double*, double, double*, double*, ob_orbele*)
liborbele.rec2kep.argtypes = [np_vector3, np_vector3,
                              ctypes.c_double, np_vector3, np_vector3,
                              ob_orbele_p]
liborbele.rec2kep.restype = ctypes.c_int
def rec2kep(r_bar, v_bar,
            eps, h_bar, e_bar):
    kep = ob_orbele()
    if liborbele.rec2kep(r_bar, v_bar,
                         eps, h_bar, e_bar,
                         ctypes.byref(kep)) != 0:
        raise
    return (kep.sma, kep.mm, kep.ecc,
            kep.aop, kep.raan, kep.inc,
            kep.ta, kep.ea, kep.ma)

#int kep2rec(ob_orbele*, double*, double*)
liborbele.kep2rec.argtypes = [ob_orbele,
                              np_vector3, np_vector3]
liborbele.kep2rec.restype = ctypes.c_int
def kep2rec(sma, ecc, ta,
            aop, raan, inc):
    kep = ob_orbele(sma=sma, ecc=ecc, ta=ta,
                    aop=aop, raan=raan, inc=inc)
    r_bar = numpy.empty((3,), dtype=numpy.float64)
    v_bar = numpy.empty((3,), dtype=numpy.float64)
    if liborbele.kep2rec(kep, r_bar, v_bar) != 0:
        raise
    return (r_bar, v_bar)
