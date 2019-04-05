# built-in libraries
import os.path
import ctypes
import logging

# external libraries
import numpy
import numpy.ctypeslib

# internal libraries
path = os.path.dirname(__file__)
libunikep = numpy.ctypeslib.load_library('_libunikep', path)

# exports
__all__ = (
    'settol', 'setmaxiter',
    'setmu', 'unikep'
)

# constants
#  ...

# types
c_double_p = ctypes.POINTER(ctypes.c_double)
np_vector3 = numpy.ctypeslib.ndpointer(dtype=numpy.float64,
                                       ndim=1, shape=(3,),
                                       flags='C')


# int settol(double)
libunikep.settol.argtypes = [ctypes.c_double]
libunikep.settol.restype = ctypes.c_int
def settol(tol):
    if libunikep.settol(tol) != 0:
        raise


# int setmaxiter(int)
libunikep.setmaxiter.argtypes = [ctypes.c_int]
libunikep.setmaxiter.restype = ctypes.c_int
def setmaxiter(maxiter):
    if libunikep.setmaxiter(maxiter) != 0:
        raise


# int setmu(double)
libunikep.setmu.argtypes = [ctypes.c_double]
libunikep.setmu.restype = ctypes.c_int
def setmu(mu):
    if libunikep.setmu(mu) != 0:
        raise


# int stumpff(double, double*, double*)
libunikep.stumpff.argtypes = [
    ctypes.c_double, c_double_p, c_double_p
]
libunikep.stumpff.restype = ctypes.c_int
def stumpff(z):
    C = ctypes.c_double()
    S = ctypes.c_double()
    if libunikep.stumpff(
        z,  ctypes.byref(C), ctypes.byref(S)
    ) != 0:
        raise
    return (C.value, S.value)


# int unikep(double*, double*, double*, double*, double)
libunikep.unikep.argtypes = [
    np_vector3, np_vector3,
    np_vector3, np_vector3,
    ctypes.c_double
]
libunikep.unikep.restype = ctypes.c_int
def unikep(r0_bar, v0_bar, t):
    r_bar = numpy.empty_like(r0_bar)
    v_bar = numpy.empty_like(v0_bar)
    if libunikep.unikep(
        r0_bar, v0_bar, r_bar, v_bar, t
    ) != 0:
        raise
    return (r_bar, v_bar)
