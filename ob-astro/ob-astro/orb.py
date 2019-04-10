# built-in libraries
import math
import itertools
import collections
import logging

# external libraries
import numpy
import sgp4.earth_gravity
import sgp4.io

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.lib import libunikep, liborbele

# exports
__all__ = ("ele",
           "unikep",
           "tle2sgp", "sgp4tle",
           "inv2law",
           "rec2kep", "kep2rec",
           "apsis", "node", "pole")

# constants
MICRO = 1e-6


class OrbitalElements(collections.namedtuple
                      ("OrbitalElements",
                       ("sma", "mm", "ecc",
                        "inc", "aop", "raan",
                        "ta", "ea", "ma"))):
    pass


# ele <-> JSON
ele = Type(".orb#ele", OrbitalElements,
           OrbitalElements._asdict,
           lambda x: OrbitalElements(**x))


@Image(".orb@unikep",
       env=Node(evs=(), args=("t",),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       clk=Node(evs=(True,), args=(),
                ins=(), reqs=(),
                outs=(), pros=()),
       bod=Node(evs=(), args=("mu",),
                ins=(), reqs=(),
                outs=(), pros=()),
       orb=Node(evs=(), args=(),
                ins=(), reqs=("r_bar", "v_bar"),
                outs=(True,), pros=("r_bar", "v_bar")))
def unikep(env, clk, bod, orb):
    """Universal Kepler formulation"""
    env_t0, = next(env.data)
    mu, = next(bod.data)

    yield
    while True:
        libunikep.setmu(mu)
        
        env_t, = next(env.data)
        r_bar, v_bar = next(orb.data)
        
        r_bar, v_bar = libunikep.unikep(r_bar, v_bar, env_t - env_t0)

        orb.data.send((r_bar, v_bar))
        yield (orb.ctrl.send((True,)),)
        
        env_t0 = env_t

 
@Image(".orb@tle2sgp",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=(),
                outs=(), pros=()),
       tle=Node(evs=(), args=(),
                ins=(), reqs=(2,),
                outs=(), pros=()),
       sgp=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(4,), pros=(4,)))
def tle2sgp(env, tle, sgp):
    """Two-line elements to simple general perturbation"""
    yield
    two, = next(tle.data)
    four = sgp4.io.twoline2rv(two[1], two[2],
                              sgp4.earth_gravity.wgs84)
    sgp.data.send((four,))
    yield (sgp.ctrl.send((True,)),)

      
@Image(".orb@sgp4tle",
       clk=Node(evs=(8601,), args=(),
                ins=(), reqs=("t_dt",),
                outs=(), pros=()),
       sgp=Node(evs=(), args=(),
                ins=(), reqs=(4,),
                outs=(), pros=()),
       orb=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(True,), pros=("r_bar", "v_bar")))
def sgp4tle(clk, sgp, orb):
    """Simple general perturbation for two-line elements"""
    yield
    while True:        
        clk_t, = next(clk.data)
        four, = next(sgp.data)
        r_bar, v_bar = four.propagate(clk_t.year, clk_t.month, clk_t.day,
                                      clk_t.hour, clk_t.minute,
                                      clk_t.second + clk_t.microsecond * MICRO)
        orb.data.send((r_bar, v_bar))
        yield (orb.ctrl.send((True,)),)

        
@Image(".orb@inv2law",
       bod=Node(evs=(), args=("mu",),
                ins=(), reqs=(),
                outs=(), pros=()),
       orb=Node(evs=(True,), args=(),
                ins=(), reqs=("r_bar", "v_bar"),
                outs=(-2,), pros=("eps", "h_bar", "e_bar")))
def inv2law(bod, orb):
    """Constants of motion"""
    mu, = next(bod.data)

    yield
    while True:
        liborbele.setmu(mu)

        r_bar, v_bar = next(orb.data)
        eps, h_bar, e_bar = liborbele.inv2law(r_bar, v_bar)
        orb.data.send((eps, h_bar, e_bar))
        yield (orb.ctrl.send((True,)),)


@Image(".orb@rec2kep",
       bod=Node(evs=(), args=("mu",),
                ins=(), reqs=(),
                outs=(), pros=()),
       orb=Node(evs=(-2,), args=(),
                ins=(True, -2,), reqs=("r_bar", "v_bar",
                                       "eps", "h_bar", "e_bar"),
                outs=(6,), pros=("kep",)))
def rec2kep(bod, orb):
    """State vectors to Kepler elements"""
    mu, = next(bod.data)

    evs = yield
    while True:
        liborbele.setmu(mu)

        orb_e, inv_e = next(orb.ctrl)
        if orb_e in evs and inv_e in evs:
            r_bar, v_bar, eps, h_bar, e_bar = next(orb.data)
            kep = OrbitalElements(*liborbele.rec2kep
                                  (r_bar, v_bar,
                                   eps, h_bar, e_bar))
            orb.data.send((kep,))
            yield (orb.ctrl.send((True,)),)
        else:
            orb.data.send(None)
            yield (orb.ctrl.send(None),)


@Image(".orb@kep2rec",
       bod=Node(evs=(), args=("mu",),
                ins=(), reqs=(),
                outs=(), pros=()),
       orb=Node(evs=(6,), args=(),
                ins=(), reqs=("kep",),
                outs=(True,), pros=("r_bar", "v_bar")))
def kep2rec(bod, orb):
    """Kepler elements to state vectors"""
    mu, = next(bod.data)

    yield
    while True:
        liborbele.setmu(mu)

        kep, = next(orb.data)
        r_bar, v_bar = liborbele.kep2rec(kep.sma, kep.ecc, kep.ta,
                                         kep.aop, kep.raan, kep.inc)
        orb.data.send((r_bar, v_bar))
        yield (orb.ctrl.send((True,)),)


@Image(".orb@apsis",
       env=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=("lim", "tol"),
                ins=(), reqs=(),
                outs=(), pros=()),
       clk=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(False,), pros=("t",)),
       orb=Node(evs=(6,), args=(),
                ins=(), reqs=("kep",),
                outs=("peri", "apo"),
                pros=("tperi", "tapo")))
def apsis(env, sys, clk, orb):
    """Apsis crossing"""
    lim, tol = next(env.data)

    yield
    while True:
        t0,  = next(env.data) 
        kep, = next(orb.data)

        # periapsis and apoapsis
        tp = t0 + (2 * math.pi - kep.ma) / kep.mm
        ta = ((t0 + (math.pi - kep.ma) / kep.mm)
              if kep.ma < math.pi else
              (t0 + (3 * math.pi - kep.ma) / kep.mm))
        
        if min(abs(tp - t0), abs((ta - t0) - (tp + t0) / 2)) < tol:
            t1 = ta  # at periapsis
            p, a = True, None
        elif min(abs(ta - t0), abs((tp - t0) - (ta + t0) / 2)) < tol:
            t1 = tp  # at apoapsis
            p, a = None, True
        else:
            t1 = min(tp, ta)
            p, a = None, None
            
        t = t1 if abs(t1 - t0) < lim else None
        e = t is not None
        
        orb.data.send((t,))
        orb.data.send((tp, ta))
        yield (clk.ctrl.send((e,)),
               orb.ctrl.send((p, a)))


@Image(".orb@node",
       env=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=("lim", "tol"),
                ins=(), reqs=(),
                outs=(), pros=()),
       clk=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(False,), pros=("t",)),
       orb=Node(evs=(6,), args=(),
                ins=(), reqs=("kep",),
                outs=("asc", "desc"),
                pros=("tasc", "tdesc")))
def node(env, sys, clk, orb):
    """Node crossing"""
    lim, tol = next(env.data)

    yield
    while True:
        t0,  = next(env.data) 
        kep, = next(orb.data)

        # ascending node
        ta1 = 2 * (2 * math.pi - kep.aop
                   if kep.ta + kep.aop < 2 * math.pi  else
                   4 * math.pi - kep.aop)
        ea1 = 2 * math.atan2(math.sqrt(1 - kep.ecc) * math.sin(ta1 / 2),
                             math.sqrt(1 + kep.ecc) * math.cos(ta1 / 2))
        ma1 = ea1 - kep.ecc * math.sin(ea1)
        ta = (ma1 - kep.ma) / kep.mm

        # descending node
        ta1 = (math.pi - kep.aop
               if kep.ta + kep.aop < math.pi else
               3 * math.pi - kep.aop
               if kep.ta + kep.aop < 3 * math.pi else
               5 * math.pi - kep.aop)
        ea1 = 2 * math.atan2(math.sqrt(1 - kep.ecc) * math.sin(ta1 / 2),
                             math.sqrt(1 + kep.ecc) * math.cos(ta1 / 2))
        ma1 = ea1 - kep.ecc * math.sin(ea1)
        td = (ma1 - kep.ma) / kep.mm

        if kep.inc > math.pi / 2:
            td, ta = ta, td
        
        if min(abs(ta - t0), abs((td - t0) - (ta + t0) / 2)) < tol:
            t1 = td  # at ascending node
            a, d = True, None
        elif min(abs(td - t0), abs((ta - t0) - (td + t0) / 2)) < tol:
            t1 = ta  # at descending node
            a, d = None, True
        else:
            t1 = min(ta, td)
            a, d = None, None
            
        t = t1 if abs(t1 - t0) < lim else None
        e = t is not None
        
        orb.data.send((t,))
        orb.data.send((ta, td))
        yield (clk.ctrl.send((e,)),
               orb.ctrl.send((a, d)))


@Image(".orb@pole",
       env=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=("lim", "tol"),
                ins=(), reqs=(),
                outs=(), pros=()),
       clk=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=(False,), pros=("t",)),
       orb=Node(evs=(6,), args=(),
                ins=(), reqs=("kep",),
                outs=("north", "south"),
                pros=("tnorth", "tsouth")))
def pole(env, sys, clk, orb):
    """Pole crossing"""
    lim, tol = next(env.data)

    yield
    while True:
        t0,  = next(env.data) 
        kep, = next(orb.data)
        mm, ecc, aop, inc, ma = kep.mm, kep.ecc, kep.aop, kep.inc, kep.ma

        # north pole
        ta1 = 2 * (math.pi / 2 - kep.aop
                   if kep.ta + kep.aop < math.pi / 2 else
                   5 * math.pi / 2 - kep.aop
                   if kep.ta + kep.aop < 5 * math.pi / 2 else
                   9 * math.pi / 2 - kep.aop)
        ea1 = 2 * math.atan2(math.sqrt(1 - ecc) * math.sin(ta1 / 2),
                             math.sqrt(1 + ecc) * math.cos(ta1 / 2))
        ma1 = ea1 - ecc * math.sin(ea1)
        ta = (ma1 - ma) / mm

        # south pole
        ta1 = (math.pi - kep.aop
               if kep.ta + kep.aop < 3 * math.pi / 2 else
               3 * math.pi / 2 - kep.aop
               if kep.ta + kep.aop < 7 * math.pi / 2 else
               7 * math.pi - kep.aop)
        ea1 = 2 * math.atan2(math.sqrt(1 - ecc) * math.sin(ta1 / 2),
                             math.sqrt(1 + ecc) * math.cos(ta1 / 2))
        ma1 = ea1 - ecc * math.sin(ea1)
        td = (ma1 - ma) / mm

        if kep.inc > math.pi / 2:
            ts, tn = tn, ts
        
        if min(abs(tn - t0), abs((ts - t0) - (tn + t0) / 2)) < tol:
            t1 = ts  # at north pole
            n, s = True, None
        elif min(abs(ts - t0), abs((tn - t0) - (ts + t0) / 2)) < tol:
            t1 = tn  # at south pole
            n, s = None, True
        else:
            t1 = min(tn, ts)
            n, s = None, None
            
        t = t1 if abs(t1 - t0) < lim else None
        e = t is not None
        
        orb.data.send((t,))
        orb.data.send((tn, ts))
        yield (clk.ctrl.send((e,)),
               orb.ctrl.send((n, s)))
