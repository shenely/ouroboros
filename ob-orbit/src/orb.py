#built-in libraries
from math import sqrt, cos, sin, cosh, sinh
import logging

#external libraries
import numpy
import scipy.linalg

#internal libraries
from ouroboros import HIGH, NORMAL, coroutine, Item, PROCESS

#exports
__all__ = ['unikep']

#constants
#...

#helper functions
def stumpff(z):
    return (((sqrt(z) - sin(sqrt(z))) / sqrt(z) ** 3,
             (1 - cos(sqrt(z))) / z)
            if z > 0 else
            ((sinh(sqrt(-z)) - sqrt(-z)) / sqrt(-z) ** 3,
             (1 - cosh(sqrt(-z))) / z)
            if z < 0 else
            (1.0 / 6.0, 1.0 / 2.0))
@coroutine
def universal_kepler(mu, tol=1.48e-8, maxiter=50):
    sqrt_mu = sqrt(mu)
    dt, r0_bar, v0_bar = yield
    while True:
        r0 = scipy.linalg.norm(r0_bar)
        v0 = scipy.linalg.norm(v0_bar)
        r0_dot_v0 = numpy.dot(r0_bar, v0_bar)
        alpha = 2 / r0 - v0 * v0 / mu
        chi = sqrt_mu * abs(alpha) * dt
        for i in xrange(maxiter):
            chi__2 = chi * chi
            chi__3 = chi * chi__2
            z = alpha * chi__2
            S, C = stumpff(z)
            f = (r0_dot_v0 * chi__2 * C / sqrt_mu +
                 (1 - alpha * r0) * chi__3 * S +
                 r0 * chi - sqrt_mu * dt)
            fprime = (r0_dot_v0 * chi * (1 - z * S) / sqrt_mu +
                      (1 - alpha * r0) * chi__2 * C + r0)
            delta = f / fprime
            if abs(delta) < tol:break
            else:chi -= delta
        else:pass#warning
        f = 1 - chi__2 * C / r0
        g = dt - chi__3 * S / sqrt_mu
        r_bar = f * r0_bar + g * v0_bar
        r = scipy.linalg.norm(r_bar)
        f_dot = sqrt_mu * chi * (z * S - 1) / (r * r0)
        g_dot = 1 - chi__2 * C / r
        v_bar = f_dot * r0_bar + g_dot * v0_bar
        dt, r0_bar, v0_bar = yield r_bar, v_bar

##def true2ecc(th_rad, e):
##    E_rad = 2 * atan(sqrt((1 - e) / (1 + e)) * tan(th_rad / 2))
##    
##    return E_rad
##
##def ecc2true(E_rad, e):
##    th_rad = 2 * atan(sqrt((1 + e) / (1 - e)) * tan(E_rad / 2))
##    
##    return th_rad
##
##def ecc2mean(E_rad, e):
##    M_rad = E_rad - e * sin(E_rad)
##    
##    return M_rad
##
##def mean2ecc(M_rad, e):
##    E_rad = newton(lambda E, M, e: E - e * sin(E) - M, M_rad,
##                   fprime=lambda E, M, e: 1 - e * cos(E))
##    
##    return E_rad

@PROCESS('orb.unikep', HIGH,
         Item('clock',
              evs=('tick',), args=('t',),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('body',
              evs=(), args=('mu',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('orbit',
              evs=(), args=(),
              ins=('rec',), reqs=('r_bar', 'v_bar'),
              outs=('rec',), pros=('r_bar', 'v_bar')))
def unikep(clk, bod, orb):
    """Propagate orbits"""
    clk_t0, = clk.next()
    mu, = bod.next()
    newton = universal_kepler(mu)
    clk, usr, orb = yield
    while True:
        (clk_t,), (clk_e,) = clk.next()
        dt = clk_t - clk_t0
        orb = (((logging.info('%r, %r', r_bar, v_bar) or
                 (newton.send((dt, r_bar, v_bar)), (True,))
                 if not orb_e else
                 ((None, None), (False,)))
                for (r_bar, v_bar), (orb_e,) in orb)
               if clk_e else None)
        clk, bod, orb = yield None, None, orb
        clk_t0 = clk_t

##@PROCESS('orb.rec2orb', NORMAL,
##         Item('body',
##              evs=(), args=('mu',),
##              ins=(), reqs=(),
##              outs=(), pros=()),
##         Item('orbit',
##              evs=('rec',), args=(),
##              ins=('rec', 'orb'), reqs=('r_bar', 'v_bar'),
##              outs=('orb',), pros=('eps', 'h_vec', 'e_vec')))
##def rec2orb(bod, orb):
##    mu, = bod.next()
##    bod, orb = yield    
##    while True:
##        orb = (((r_bar, v_bar,
##                 norm(r_bar), norm(v_bar),
##                 cross(r_bar, v_bar))
##                if rec_e and not orb_e else
##                (None, None, None, None, None))
##               for (r_bar, v_bar), (rec_e, orb_e) in orb)
##        orb = (((v ** 2 / 2 - mu / r,
##                 h_bar,
##                 cross(v_bar, h_bar) / mu - r_bar / r)
##                if r_bar is not None else
##                (None, None, None))
##               for r_bar, v_bar, r, v, h_bar in orb)
##        orb = ((((eps, h_bar, e_bar), (True,))
##                if eps is not None else
##                ((None, None, None), (False,)))
##               for eps, h_bar, e_bar in orb)
##        bod, orb = yield None, orb
##
##@Process("orb.sph2kep",
##         ([], ["sph"], [], ["r", "az", ], []),#pqw
##         ([], [], [], ["r", "az", "el"], []),#apse
##         ([], [], [], ["az", "el"], []),#pole
##         ([], [], {"kep":True}, [], ["a", "M", "e", "om", "i", "OM"]))#elements
##def sph2kep():
##    a = M = e = om = i = OM = None
##
##    while True:
##        #Input/output
##        r, th, e, az, el, OM, i = yield a, M, e, om, i, OM,
##        
##        #Semi-major axis
##        a = r * (1 + e * cos(th)) / (1 - e ** 2)#from orbit equation
##
##        #True anomaly to...
##        E = true2ecc(th, e)#...eccentric anonaly
##        M = ecc2mean(E, e)#...mean anomaly
##
##        #Argument of periapsis
##        om = asin(sin(el) / cos(i))#from eccentricity vector
##        om = (pi - om) if pi / 2 < az < 3 * pi / 2 else om
##
##        #Inclination
##        i = pi / 2 - i#from angular momentum elevation
##
##        #Right ascension of the ascending node
##        OM += pi / 2#from angular momentum azimuth
##        
##        print a, M, e, om, i, OM
