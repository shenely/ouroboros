#built-in libraries
import math
import logging

#external libraries
import numpy
import sgp4.earth_gravity
import sgp4.io

#internal libraries
from ouroboros import REGISTRY, NORMAL, Item, PROCESS
from ouroboros.lib import (libunikep,
                           liborbele)

#exports
__all__ = ('unikep',
           'tle2sgp', 'sgp4tle',
           'inv2law',
           'rec2kep', 'kep2rec',
           'apsis', 'pole', 'node')

#constants
MICRO = 1e-6

@PROCESS('orb.unikep', NORMAL,
         Item('env',
              evs=(), args=('t',),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('clk',
              evs=('tock',), args=(),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=(), args=(),
              ins=(), reqs=('r_bar', 'v_bar'),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def unikep(env, clk, bod, orb):
    """Universal Kepler formulation"""
            
    env_t0, = env.next()
    mu, = bod.next()

    right = yield
    while True:
        env, orb = (right['env'],
                    right['orb'])
        
        (env_t,), _ = env.next()
        libunikep.setmu(mu)
        orb = ((libunikep.unikep(r0_bar, v0_bar,
                                 env_t - env_t0), (True,))
               for (r0_bar, v0_bar), _ in orb)
        env_t0 = env_t

        left = {'orb': orb}
        right = yield left
        
@PROCESS('orb.tle2sgp', NORMAL,
         Item('env',
              evs=(True,), args=(),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('tle',
              evs=(), args=(2,),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sgp',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=(4,), pros=(4,)))
def tle2sgp(env, tle, sgp):
    """Two-line elements to simple general perturbation"""

    yield
    sgp = (((sgp4.io.twoline2rv
             (tle[1], tle[2],
              sgp4.earth_gravity.wgs84),), (True,))
           for (tle,) in tle)
    
    left = {'sgp': sgp}
    yield left
        
@PROCESS('orb.sgp4tle', NORMAL,
         Item('clk',
              evs=(8601,), args=(),
              ins=(), reqs=('t_dt',),
              outs=(), pros=()),
         Item('sgp',
              evs=(), args=(),
              ins=(), reqs=(4,),
              outs=(), pros=()),
         Item('orb',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def sgp4tle(clk, sgp, orb):
    """Simple general perturbation for two-line elements"""
    right = yield
    while True:
        clk, sgp = (right['clk'],
                    right['sgp'])
        
        (clk_t,), _ = clk.next()
        orb = ((map(numpy.array,
                    sgp.propagate
                    (clk_t.year, clk_t.month, clk_t.day,
                     clk_t.hour, clk_t.minute, clk_t.second +
                     clk_t.microsecond * MICRO)), (True,))
               for (sgp,), _ in sgp)

        left = {'orb': orb}
        right = yield left
        
@PROCESS('orb.inv2law', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=('rec',), args=(),
              ins=('rec',), reqs=('r_bar', 'v_bar'),
              outs=(-2,), pros=('eps', 'h_bar', 'e_bar')))
def inv2law(bod, orb):
    """Constants of motion"""
    mu, = bod.next()

    right = yield
    while True:
        orb = right['orb']
        
        liborbele.setmu(mu)
        orb = (((liborbele.inv2law(r_bar, v_bar), (True,))
                if rec_e else
                (None, None))
               for (r_bar, v_bar), (rec_e,) in orb)
        
        left = {'orb': orb}
        right = yield left

@PROCESS('orb.rec2kep', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=(-2,), args=(),
              ins=('rec', -2,), reqs=('r_bar', 'v_bar',
                                      'eps', 'h_bar', 'e_bar'),
              outs=('kep',), pros=('sma', 'mm', 'ecc',
                                   'inc', 'aop', 'raan',
                                   'ta', 'ea', 'ma')))
def rec2kep(bod, orb):
    """State vectors to Kepler elements"""
    mu, = bod.next()

    right = yield
    while True:
        orb = right['orb']
        
        liborbele.setmu(mu)
        orb = (((liborbele.rec2kep(r_bar, v_bar,
                                   eps, h_bar, e_bar), (True,))
                if rec_e and law_e else
                (None, None))
               for _, (rec_e, law_e) in orb)
        
        left = {'orb': orb}
        right = yield left

@PROCESS('orb.kep2rec', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=('kep',), args=(),
              ins=('kep',), reqs=('sma', 'ecc', 'ta',
                                  'aop', 'raan', 'inc'),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def kep2rec(bod, orb):
    """Kepler elements to state vectors"""
    mu, = bod.next()

    right = yield
    while True:
        orb = right['orb']
        
        liborbele.setmu(mu)
        orb = (((liborbele.kep2rec(sma, ecc, ta,
                                   aop, raan, inc), (True,))
                if kep_e else
                (None, None))
               for (sma, ecc, ta,
                    aop, raan, inc), (kep_e,) in orb)
        
        left = {'orb': orb}
        right = yield left

@PROCESS('orb.apsis', NORMAL,
         Item('env',
              evs=(), args=(),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('orb',
              evs=('kep',), args=(),
              ins=('kep',), reqs=('mm', 'ma'),
              outs=('peri', 'apo'), pros=('t_peri', 't_apo')))
def apsis(env, orb):
    """Apsis crossing"""
    right = yield
    while True:
        env, orb = (right['env'],
                    right['orb'])

        (env_t,), _  = env.next()
        orb = ((((t + (2 * pi - ma) / mm,
                  (t + (pi - ma) / mm)
                  if ma < pi else
                  (t + (3 * pi - ma) / mm))
                 (False, False))
                if kep_e is True else
                (None, None))
               for (mm, ma), (kep_e,) in orb)
        
        left = {'orb': orb}
        right = yield left

@PROCESS('orb.node', NORMAL,
         Item('env',
              evs=(), args=(),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('orb',
              evs=('kep',), args=(),
              ins=('kep',), reqs=('mm', 'ma'),
              outs=('asc', 'desc'), pros=('t_asc', 't_desc')))
def node(env, orb):
    """Node crossing"""
    mu, = bod.next()

    right = yield
    while True:
        env, orb = (right['env'],
                    right['orb'])

##        ta1 = 2 * pi - aop
##        ta1 = pi - aop
##        ea1 = 2 * atan2(sqrt(1 - ecc) * sin(ta1 / 2),
##                        sqrt(1 + ecc) * cos(ta1 / 2))
##        ma1 = ea1 - ecc * sin(ea1)
##        t = (ma1 - ma) / mm
        

        (env_t,), _  = env.next()
        orb = ((((t + (2 * pi - ma) / mm,
                  (t + (pi - ma) / mm)
                  if ma < pi else
                  (t + (3 * pi - ma) / mm))
                 (False, False))
                if kep_e is True else
                (None, None))
               for (mm, ma), (kep_e,) in orb)
        
        left = {'orb': orb}
        right = yield left
