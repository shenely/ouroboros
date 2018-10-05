#built-in libraries
import math
import random

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('model', 'sensor', 'actor')

#constants
#...

#commands
#RW_ON
#RW_OFF
#RW_SET

#telemetry
#(enum) RW_STATE
#(lin) RW_SIGN
#(lin) RW_DUTY
#(lin) RW_CURR
#(lin) RW_VOLT
#(lin) RW_TEMP
#(lin) RW_RATE
#(lin) RW_ANGMOM
#(lin) RW_TORQUE

@PROCESS('rw.model', NORMAL,
         Item('env',
              evs=(), args=('t',),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('rail',
              evs=(), args=('v',),
              ins=(), reqs=('v',),
              outs=(), pros=()),
         Item('wire',
              evs=(), args=('i',),
              ins=(), reqs=('i',),
              outs=(), pros=()),
         Item('rw',
              evs=(True,), args=('_hat',
                                 'I', 'C', 'k',
                                 's', 'om', 'tau', 'T'),
              ins=(), reqs=('s',),
              outs=(), pros=('om', 'tau', 'T',
                             'L', 'L_bar')),
         Item('ctlr',
              evs=(True,), args=(),
              ins=(), reqs=('s',),
              outs=(), pros=()))
def model(env, rail, wire, rw):
    """Reaction wheel model"""
    (t0,) = env.next()
    (v,) = rail.next()
    (i,) = wire.next()
    (_hat, I, C, k,
     s, om, tau, T) = rw.next()
    
    right = yield
    while True:
        env, rail, wire, rw = (right['env'],
                               right['rail'],
                               right['wire'],
                               right['rw'])
        (t,), _ = env.next()
        
        om += s * (tau / I) * (t - t0)
        L = I * om
        L_bar = L * _hat
        T += C * i * v * (t - t0)
        
        (v,), _ = rail.next()
        (i,), _ = wire.next()
        (s,), _ = rw.next()
        
        tau = k * i
        t0 = t
        
        rw = (((om, tau, T,
                L, L_bar), ()),)
        left = {'rw': rw}
        right = yield left

@PROCESS('rw.sensor', NORMAL,
         Item('env',
              evs=(), args=('t',),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('rw',
              evs=(), args=(),
              ins=(), reqs=('om',),
              outs=(), pros=()),
         Item('obsr',
              evs=(True,), args=(),
              ins=(), reqs=(),
              outs=(), pros=('om',)))
def sensor(env, rw, obsr):
    """Reaction wheel sensor"""
    (t0,) = env.next()
    f = (2 * math.pi) * random.random()
    
    right = yield
    while True:
        env, rw = (right['env'],
                   right['rw'])
        (t,), _ = env.next()
        (om,), _ = rw.next()

        n, f = divmod(f + om * (t - t0), 2 * math.pi)
        _om = 2 * math.pi * n / (t - t0)
        t0 = t
        
        obsr = (((_om,), ()),)
        left = {'obsr': obsr}
        right = yield left

@PROCESS('rw.actor', NORMAL,
         Item('rail',
              evs=(), args=(),
              ins=(), reqs=('v',),
              outs=(), pros=()),
         Item('wire',
              evs=(), args=('R',),
              ins=(), reqs=(),
              outs=(), pros=('i',)),
         Item('rw',
              evs=(), args=('k',),
              ins=(), reqs=(),
              outs=(), pros=('s', 'd')),
         Item('obsr',
              evs=(), args=(),
              ins=(), reqs=('om',),
              outs=(), pros=()),
         Item('ctlr',
              evs=(True,), args=('K',),
              ins=(), reqs=('om',),
              outs=(), pros=()))
def actor(rail, wire, rw, obsr, ctlr):
    """Reaction wheel actor"""
    (A,) = rw.next()
    (R,) = wire.next()
    (K,) = ctlr.next()
    
    right = yield
    while True:
        rail, obsr, ctlr = (right['rail'],
                            right['obsr'],
                            right['ctlr'])
        (v,), _ = rail.next()
        (_om,), _ = obsr.next()
        (om_,), _ = ctlr.next()

        u = K * (om_ - _om) + (A / v) * om_
        d = abs(u)#duty cycle
        s = int(u / d)#switch sign

        i = (d * v - s * A * _om) / R
        
        wire = (((i,), ()),)
        rw = (((s, d,), ()),)
        left = {'wire': wire,
                'rw': rw}
        right = yield left
