# built-in libraries
import math

# external libraries
import numpy
import scipy.linalg

# internal libraries
from ouroboros import Type, Image, Node

# exports
__all__ = ("force", "torque",
           "point", "e2pol", "m2pol")

# constants
SPEED_OF_LIGHT = 299792458.0  # m/s
MAGNETIC_CONST = 4 * math.pi * 10e-7  # H/m
ELECTRIC_CONST = 1 / MAGNETIC_CONST / SPEED_OF_LIGHT ** 2  # F/m


@Image(".phys.em@force",
       usr=Node(evs=(), args=("q"),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "r_bar", "v_bar"),
                outs=(False,), pros=("F_bar",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("E_bar", "B_bar"),
               outs=(True,), pros=("t", "r_bar", "v_bar")))
def force(usr, fun, **kw):
    """Lorentz force"""
    q, = usr.args
    
    evs = yield
    while True:
        e, = fun.ins()
        t, r_bar, v_bar = fun.reqs
        F_bar = numpy.zeros_like(v_bar)

        for sub in kw.values():
            sub.pros = t, r_bar, v_bar
            yield (sub.outs((e in evs,)),)
            E_bar, B_bar = sub.reqs
            F_bar += q * (E_bar + numpy.cross(v_bar, B_bar))
        else:
            fun.pros = F_bar,
            yield (fun.outs((e in evs,)),)


@Image(".phys.em@torque",
       usr=Node(evs=(), args=("p_bar", "m_bar"),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "r_bar", "v_bar"),
                outs=(False,), pros=("M_bar",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("t", "r_bar", "v_bar"),
               outs=(True,), pros=("E_bar", "B_bar")))
def torque(usr, fun, **kw):
    """Dipole torques"""
    p_bar, m_bar = usr.args
    
    evs = yield
    while True:
        e, = fun.ins()
        t, r_bar, v_bar = fun.reqs
        M_bar = numpy.zeros_like(v_bar)

        for sub in kw.values():
            sub.pros = t, r_bar, v_bar
            yield (sub.outs((e in evs,)),)
            E_bar, B_bar = sub.reqs
            M_bar += (numpy.cross(p_bar, E_bar) +
                      numpy.cross(m_bar, B_bar))
        else:
            fun.pros = M_bar,
            yield (fun.outs((e in evs,)),)


@Image(".phys@que",
       nil=Node(evs=(), args=("q",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()),
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar",),
                outs=(False,), pros=("E_bar",)))
def point(nil, one):
    """Point charge"""
    C = 1 / (4 * math.pi / ELECTRIC_CONST)  # N*m2/C2
    q, = usr.args

    evs = yield
    while True:
        r0_bar, = nil.reqs
        r1_bar, = one.reqs
        e, = one.ins()
        
        r_bar = r1_bar - r0_bar
        E_bar = - C * q * r_bar / scipy.linalg.norm(r_bar) ** 3
        
        one.pros = E_bar,
        yield (one.outs((e in evs,)),)


@Image(".phys@e2pol",
       nil=Node(evs=(), args=("p_bar",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()),
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar",),
                outs=(False,), pros=("E_bar",)))
def e2pol(nil, one):
    """Electric dipole"""
    C = 1 / (4 * math.pi / ELECTRIC_CONST)  # m/F
    p_bar, = nil.args

    evs = yield
    while True:
        r0_bar, = nil.reqs
        r1_bar, = one.reqs
        e, = one.ins()
        
        r_bar = r1_bar - r0_bar
        r = scipy.linalg.norm(r_bar)
        r_hat = r_bar / r
        B_bar = C * (3 * numpy.dot(p_bar, r_hat) * r_hat - p_bar) / r ** 3
        
        one.pros = E_bar,
        yield (one.outs((e in evs,)),)


@Image(".phys@m2pol",
       nil=Node(evs=(), args=("m_bar",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()),
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar",),
                outs=(False,), pros=("B_bar",)))
def m2pol(nil, one):
    """Magnetic dipole"""
    C = MAGNETIC_CONST / (4 * math.pi)  # m/H
    m_bar, = nil.args

    evs = yield
    while True:
        r0_bar, = nil.reqs
        r1_bar, = one.reqs
        e, = one.ins()
        
        r_bar = r1_bar - r0_bar
        r = scipy.linalg.norm(r_bar)
        r_hat = r_bar / r
        B_bar = C * (3 * numpy.dot(m_bar, r_hat) * r_hat - m_bar) / r ** 3
        
        one.pros = B_bar,
        yield (one.outs((e in evs,)),)
