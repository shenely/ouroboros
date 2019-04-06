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
__all__ = ("unikep",
           "tle2sgp", "sgp4tle",
           "inv2law",
           "rec2kep", "kep2rec",)
##           "apsis", "pole", "node")

# constants
MICRO = 1e-6


class Elements(collections.namedtuple
               ("Elements",
                ("sma", "mm", "ecc",
                 "inc", "aop", "raan",
                 "ta", "ea", "ma"))):
    pass


# ele <-> JSON
ele = Type(".orb#ele", Elements,
           Elements._asdict,
           lambda x: Elements(**x))


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
    env_t0, = env.data.next()
    mu, = bod.data.next()

    yield
    while True:
        libunikep.setmu(mu)
        
        env_t, = env.data.next()
        r_bar, v_bar = orb.data.next()
        
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
    two, = tle.data.next()
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
        clk_t, = clk.data.next()
        four, = sgp.data.next()
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
    mu, = bod.data.next()

    yield
    while True:
        liborbele.setmu(mu)

        r_bar, v_bar = orb.data.next()
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
    mu, = bod.data.next()

    evs = yield
    while True:
        liborbele.setmu(mu)

        orb_e, inv_e = orb.ctrl.next()
        if orb_e in evs and inv_e in evs:
            r_bar, v_bar, eps, h_bar, e_bar = orb.data.next()
            kep = Elements(*liborbele.rec2kep
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
                ins=(6,), reqs=("kep",),
                outs=(True,), pros=("r_bar", "v_bar")))
def kep2rec(bod, orb):
    """Kepler elements to state vectors"""
    mu, = bod.data.next()

    evs = yield
    while True:
        liborbele.setmu(mu)

        kep, = orb.data.next()
        r_bar, v_bar = liborbele.kep2rec(kep.sma, kep.ecc, kep.ta,
                                         kep.aop, kep.raan, kep.inc)
        orb.data.send((r_bar, v_bar))
        yield (orb.ctrl.send((True,)),)


##@Image(
##    "orb.apsis",
##    env=Node(
##        evs=(), args=(),
##        ins=(), reqs=("t",),
##        outs=(), pros=()),
##    orb=Node(
##        evs=(6,), args=(),
##        ins=(6,), reqs=("mm", "ma"),
##        outs=("peri", "apo"), pros=("peri", "apo")))
##def apsis(env, orb):
##    """Apsis crossing"""
##    evs = yield
##    while True:
##        env_t,  = env.data.next() 
##        
##        yield (
##            orb.data.send(
##                (
##                    env_t + (2 * pi - ma) / mm,
##                    (env_t + (pi - ma) / mm)
##                    if ma < pi else
##                    (env_t + (3 * pi - ma) / mm)
##                )
##                if kep_e in evs
##                else None
##            ) or
##            orb.ctrl.send(None)
##            for _, (mm, ma), (kep_e,) in itertools.izip(orb)
##        )
##
##
##@Image(
##    "orb.node",
##    env=Node(
##        evs=(), args=(),
##        ins=(), reqs=("t",),
##        outs=(), pros=()
##    ),
##    orb=Node(
##        evs=("kep",), args=(),
##        ins=("kep",), reqs=("mm", "ma"),
##        outs=("asc", "desc"), pros=("t_asc", "t_desc")
##    )
##)
##def node(env, orb):
##    """Node crossing"""
##    mu, = bod.next()
##
##    evs = yield
##    while True:
##
####        ta1 = 2 * pi - aop
####        ta1 = pi - aop
####        ea1 = 2 * atan2(sqrt(1 - ecc) * sin(ta1 / 2),
####                        sqrt(1 + ecc) * cos(ta1 / 2))
####        ma1 = ea1 - ecc * sin(ea1)
####        t = (ma1 - ma) / mm
##        
##
##        (env_t,), _  = env.next()
##        orb = ((((t + (2 * pi - ma) / mm,
##                  (t + (pi - ma) / mm)
##                  if ma < pi else
##                  (t + (3 * pi - ma) / mm))
##                 (False, False))
##                if kep_e is True else
##                (None, None))
##               for (mm, ma), (kep_e,) in orb)
##        
##        left = {"orb": orb}
##        right = yield left
