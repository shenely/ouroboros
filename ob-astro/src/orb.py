#built-in libraries
from math import (pi, sqrt,
                  cos, sin, cosh, sinh,
                  acos, asin, atan2,
                  radians)
import logging

#external libraries
import numpy
import scipy.linalg
import sgp4.earth_gravity
import sgp4.io

#internal libraries
from ouroboros import HIGH, NORMAL, coroutine, Item, PROCESS

#exports
__all__ = ('unikep',
           'tle2sgp', 'sgp4tle',
           'inv2law',
           'rec2lep', 'kep2rec')

#constants
O_BAR = numpy.array([0,0,0])
I_HAT = numpy.array([1,0,0])
J_HAT = numpy.array([0,1,0])
K_HAT = numpy.array([0,0,1])

MICRO = 1e-6

#helper functions
def stumpff(z):
    return (((sqrt(z) - sin(sqrt(z))) / sqrt(z) ** 3,
             (1 - cos(sqrt(z))) / z)
            if z > 0 else
            ((sinh(sqrt(-z)) - sqrt(-z)) / sqrt(-z) ** 3,
             (1 - cosh(sqrt(-z))) / z)
            if z < 0 else
            (1.0 / 6.0, 1.0 / 2.0))

@PROCESS('orb.unikep', HIGH,
         Item('clk',
              evs=('tick',), args=('t',),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=(), args=(),
              ins=('rec',), reqs=('r_bar', 'v_bar'),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def unikep(clk, bod, orb):
    """Universal Kepler formulation"""
    clk_t0, = clk.next()
    mu, = bod.next()

    @coroutine
    def unikep(mu, tol=1.48e-8, maxiter=50):
        sqrt_mu = sqrt(mu)
        t, r0_bar, v0_bar = yield
        while True:
            r0 = scipy.linalg.norm(r0_bar)
            v0 = scipy.linalg.norm(v0_bar)
            r0_dot_v0 = numpy.dot(r0_bar, v0_bar)
            alpha = 2 / r0 - v0 * v0 / mu
            chi = sqrt_mu * abs(alpha) * t
            for i in xrange(maxiter):
                chi__2 = chi * chi
                chi__3 = chi * chi__2
                z = alpha * chi__2
                S, C = stumpff(z)
                f = (r0_dot_v0 * chi__2 * C / sqrt_mu +
                     (1 - alpha * r0) * chi__3 * S +
                     r0 * chi - sqrt_mu * t)
                fprime = (r0_dot_v0 * chi * (1 - z * S) / sqrt_mu +
                          (1 - alpha * r0) * chi__2 * C + r0)
                delta = f / fprime
                if abs(delta) < tol:break
                else:chi -= delta
            else:pass#warning
            f = 1 - chi__2 * C / r0
            g = t - chi__3 * S / sqrt_mu
            r_bar = f * r0_bar + g * v0_bar
            r = scipy.linalg.norm(r_bar)
            f_dot = sqrt_mu * chi * (z * S - 1) / (r * r0)
            g_dot = 1 - chi__2 * C / r
            v_bar = f_dot * r0_bar + g_dot * v0_bar
            dt, r0_bar, v0_bar = yield r_bar, v_bar
    unikep = unikep(mu)

    right = yield
    while True:
        clk, orb = (right['clk'],
                    right['orb'])
        
        (clk_t,), (clk_e,) = clk.next()
        t = clk_t - clk_t0
        orb = ((((unikep.send((t, r_bar, v_bar)), (True,))
                 if not orb_e else
                 (None, (False,)))
                for (r_bar, v_bar), (orb_e,) in orb)
               if clk_e else None)
        clk_t0 = clk_t

        left = {'orb': orb}
        right = yield left
        
@PROCESS('orb.tle2sgp', HIGH,
         Item('orb',
              evs=(2,), args=(),
              ins=(2, 4), reqs=(2,),
              outs=(4,), pros=(4,)))
def tle2sgp(orb):
    """Two-line elements to simple general perturbation"""
    right = yield
    orb = right['orb']
    
    orb = ((((sgp4.io.twolin2rv
              (tle[1], tle[2],
               sgp4.earth_gravity.wgs84),), (True,))
            if two and not four else
            (None, (False,)))
           for (tle,), (two, four,) in orb)
    
    left = {'orb': orb}
    yield left
        
@PROCESS('orb.sgp4tle', HIGH,
         Item('clk',
              evs=(8601,), args=(),
              ins=(8601,), reqs=('t_dt',),
              outs=(), pros=()),
         Item('orb',
              evs=(), args=(),
              ins=('rec',), reqs=(4,),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def sgp4tle(orb):
    """Simple general perturbation for two-line elements"""
    right = yield
    while True:
        clk, orb = (right['clk'],
                    right['orb'])
        
        (clk_t,), (clk_e,) = clk.next()
        orb = ((((map(sgp.propagate
                      (clk_t.year, clk_t.month, clk_t.day,
                       clk_t.hour, t_dt.minute, clk_t.second +
                       clk_t.microsecond * MICRO),
                      numpy.array), (True,))
                 if not orb_e else
                 (None, (False,)))
                for (r_bar, v_bar), (orb_e,) in orb)
               if clk_e else None)

        left = {'orb': orb}
        right = yield left
        
@PROCESS('orb.const', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=('rec',), args=(),
              ins=('rec', 'orb'), reqs=('r_bar', 'v_bar'),
              outs=('orb',), pros=('eps', 'h_bar', 'e_bar')))
def inv2law(bod, orb):
    """Constants of motion"""
    mu, = bod.next()

    @coroutine
    def inv2law(mu):
        r_bar, v_bar  = yield
        while True:
            r = scipy.linalg.norm(r_bar)
            v = scipy.linalg.norm(v_bar)
           
            eps = v ** 2 / 2 - mu / r#<--
            h_bar = numpy.cross(r_bar, v_bar)#<--        
            e_bar = numpy.cross(v_bar, h_bar) / mu - r_bar / r#<--
            
            r_bar, v_bar = yield eps, h_bar, e_bar
    inv2law = inv2law(mu)

    right = yield
    while True:
        orb = right['orb']
        
        orb = (((inv2law.send((r_bar, v_bar)), (True,))
                if rec_e and not orb_e else
                (None, (False,)))
               for (r_bar, v_bar), (rec_e, orb_e) in orb)

        left = {'orb': orb}
        right = yield left

@PROCESS('orb.rec2kep', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orb',
              evs=('orb',), args=(),
              ins=('rec', 'orb', 'kep'), reqs=('r_bar', 'v_bar',
                                               'eps', 'h_bar', 'e_bar'),
              outs=('kep',), pros=('sma', 'mm', 'ecc',
                                   'inc', 'aop', 'raan',
                                   'ta', 'ea', 'ma')))
def rec2kep(bod, orb):
    """State vectors to Kepler elements"""
    mu, = bod.next()
    bod, orb = yield

    @coroutine
    def rec2kep(mu):
        r_bar, v_bar, eps, h_bar, e_bar = yield
        while True:
            sma = - mu / eps / 2#<--
            mm = sqrt(- 8 * eps * eps * eps) / mu#<--
            ecc = scipy.linalg.norm(e_bar)#<--
            
            r = scipy.linalg.norm(r_bar)
            h = scipy.linalg.norm(h_bar)
            n_bar = numpy.cross(K_HAT, h_bar)
            h_dot_z = numpy.dot(h_bar, K_HAT)
            e_dot_k = numpy.dot(e_bar, K_HAT)
            e_dot_r = numpy.dot(e_bar, r_bar)
            r_dot_v = numpy.dot(r_bar, v_bar)
            
            n = scipy.linalg.norm(n_bar)
            n_dot_j = numpy.dot(n_bar, J_HAT)
            n_dot_k = numpy.dot(n_bar, K_HAT)
            n_dot_e = numpy.dot(n_bar, e_bar)
            
            inc = acos(h_dot_z / h)#<--
            raan = acos(n_dot_k / n)
            aop = acos(n_dot_e / (n * ecc))
            ta = acos(e_dot_r / (ecc * r))
            
            raan = (raan if n_dot_j >= 0 else 2 * pi - raan)#<--
            aop = (aop if e_dot_k >= 0 else 2 * pi - aop)#<--
            ta = (ta if r_dot_v >= 0 else 2 * pi - ta)#<--
            
            ea = 2 * atan2(sqrt(1 - ecc) * sin(ta / 2),
                           sqrt(1 + ecc) * cos(ta / 2))#<--
            ma = ea - ecc * sin(ea)#<--
            
            (r_bar, v_bar,
             eps, h_bar, e_bar) = yield (sma, mm, ecc,
                                         inc, aop, raan,
                                         ta, ea, ma)
    rec2kep = rec2kep(mu)

    right = yield
    while True:
        orb = right['orb']
        
        orb = (((rec2kep.send((r_bar, v_bar,
                              eps, h_bar, e_bar)), (True,))
                if rec_e and orb_e and not kep_e else
                (None, (False,)))
               for ((r_bar, v_bar,
                     eps, h_bar, e_bar),
                    (rec_e, orb_e, kep_e)) in orb)

        left = {'orb': orb}
        right = yield left

@PROCESS('orb.kep2rec', NORMAL,
         Item('bod',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('kep',
              evs=(2,), args=(),
              ins=(2,), reqs=('inc', 'raan', 'ecc',
                              'aop', 'ma', 'mm'),
              outs=(), pros=()),
         Item('rec',
              evs=(), args=(),
              ins=('rec',), reqs=(),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def kep2rec(bod, tle, rec):
    """Kepler elements to state vectors"""
    mu, = bod.next()
    
    @coroutine
    def kep2rec(mu, tol=1.48e-8, maxiter=50):
        Q = numpy.empty((3,2), dtype=float)
        inc, raan, ecc, aop, ma, mm = yield
        while True:
            ea = ma if ecc < 0.8 else pi
            for i in xrange(maxiter):
                f = ea - ecc * sin(ea) - ma
                fprime = 1 - ecc * cos(ea)
                delta = f / fprime
                if abs(delta) < tol:break
                else:ea -= delta
            else:pass#warning
            ta = 2 * atan2(sqrt(1 + ecc) * sin(ea / 2),
                           sqrt(1 - ecc) * cos(ea / 2))
            sma = pow(mu / (mm * mm), 1.0 / 3.0)
            sam = sqrt(mu * sma * (1 - ecc))

            #perifocal
            cos_ta = cos(ta)
            sin_ta = sin(ta)
            r = sma * (1 - ecc * cos(ea))
            v_th = mu / sam
            r_bar = r * numpy.array([cos_ta, sin_ta])
            v_bar = v_th * numpy.array([sin_ta, ecc + cos_ta])

            cos_inc = cos(inc)
            sin_inc = sin(inc)
            cos_raan = cos(raan)
            sin_raan = sin(raan)
            cos_aop = cos(aop)
            sin_aop = sin(aop)
            Q[0,0] =   cos_raan * cos_aop - sin_raan * sin_aop * cos_inc
            Q[0,1] = - cos_raan * sin_aop - sin_raan * cos_aop * cos_inc
            Q[1,0] =   sin_raan * cos_aop + cos_raan * sin_aop * cos_inc
            Q[1,1] = - sin_raan * sin_aop + cos_raan * cos_aop * cos_inc
            Q[2,0] = sin_aop * sin_inc
            Q[2,1] = cos_aop * sin_inc

            r_bar = numpy.dot(Q, r_bar)#<--
            v_bar = numpy.dot(Q, v_bar)#<--
            
            (inc, raan, ecc,
             aop, ma, mm) = yield r_bar, v_bar
    kep2rec = kep2rec(mu)

    right = yield
    while True:
        kep, rec = (right['kep'],
                    right['rec'])
        
        rec = (((kep2rec.send((inc, raan, ecc,
                                aop, ma, mm)), (True,))
                if tle_e and not rec_e else
                (None, (False,)))
               for (((inc, raan, ecc,
                      aop, ma, mm), (kep_e,)),
                    (_, (rec_e,))) in zip(kep, rec))

        left = {'rec': rec}
        right = yield left
