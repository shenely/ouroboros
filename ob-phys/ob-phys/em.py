# built-in libraries
# ...

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
               ins=(), reqs=("t", "r_bar", "v_bar"),
               outs=(True,), pros=("E_bar", "B_bar")))
def force(usr, fun, **kw):
    """Lorentz force"""
    q, = next(usr.data)
    
    evs = yield
    while True:
        e, = next(fun.ctrl)
        t, r_bar, v_bar = next(fun.data)
        F_bar = numpy.zeros_like(v_bar)

        for sub in kw.values():
            sub.data.send((t, r_bar, v_bar))
            yield (sub.ctrl.send((e in evs,)),)
            E_bar, B_bar = next(sub.data)
            F_bar += q * (E_bar + numpy.cross(v_bar, B_bar))
        else:
            fun.data.send((F_bar,))
            yield (fun.ctrl.send((e in evs,)),)


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
    p_bar, m_bar = next(usr.data)
    
    evs = yield
    while True:
        e, = next(fun.ctrl)
        t, r_bar, v_bar = next(fun.data)
        M_bar = numpy.zeros_like(v_bar)

        for sub in kw.values():
            sub.data.send((t, r_bar, v_bar))
            yield (sub.ctrl.send((e in evs,)),)
            E_bar, B_bar = next(sub.data)
            M_bar += (numpy.cross(p_bar, E_bar) +
                      numpy.cross(m_bar, B_bar))
        else:
            fun.data.send((M_bar,))
            yield (fun.ctrl.send((e in evs,)),)


@Image(".phys@que",
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar"),
                outs=(False,), pros=("E_bar",)),
       two=Node(evs=(), args=("q",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()))
def point(one, two):
    """Point charge"""
    q, = next(two.data)
    C = q / (4 * math.pi / ELECTRIC_CONST)  # N*m2/C2

    evs = yield
    while True:
        r1_bar, = next(one.data)
        r2_bar, = next(two.data)
        e, = next(one.ctrl)
        
        r_bar = r1_bar - r2_bar
        E_bar = - C * r_bar / scipy.linalg.norm(r_bar) ** 3
        
        usr.data.send((E_bar,))
        yield (usr.ctrl.send((e in evs,)),)


@Image(".phys@e2pol",
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar"),
                outs=(False,), pros=("E_bar",)),
       two=Node(evs=(), args=("p_bar",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()))
def e2pol(one, two):
    """Electric dipole"""
    C = 1 / (4 * math.pi / ELECTRIC_CONST)  # m/F
    p_bar, = next(two.data)

    evs = yield
    while True:
        r1_bar, = next(one.data)
        r2_bar, = next(two.data)
        e, = next(one.ctrl)
        
        r_bar = r1_bar - r2_bar
        r = scipy.linalg.norm(r_bar)
        r_hat = r_bar / r
        B_bar = C * (3 * numpy.dot(p_bar, r_hat) * r_hat - p_bar) / r ** 3
        
        usr.data.send((E_bar,))
        yield (usr.ctrl.send((e in evs,)),)


@Image(".phys@m2pol",
       one=Node(evs=(True,), args=(),
                ins=(True,), reqs=("r_bar"),
                outs=(False,), pros=("B_bar",)),
       two=Node(evs=(), args=("m_bar",),
                ins=(), reqs=("r_bar",),
                outs=(), pros=()))
def m2pol(one, two):
    """Magnetic dipole"""
    C = MAGNETIC_CONST / (4 * math.pi)  # m/H
    m_bar, = next(two.data)

    evs = yield
    while True:
        r1_bar, = next(one.data)
        r2_bar, = next(two.data)
        e, = next(one.ctrl)
        
        r_bar = r1_bar - r2_bar
        r = scipy.linalg.norm(r_bar)
        r_hat = r_bar / r
        B_bar = C * (3 * numpy.dot(m_bar, r_hat) * r_hat - m_bar) / r ** 3
        
        usr.data.send((B_bar,))
        yield (usr.ctrl.send((e in evs,)),)
