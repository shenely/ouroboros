#built-in libraries
#...

#external libraries
import numpy

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('model', 'sensor', 'actor')

#constants
#...

#commands
#MT_ON
#MT_OFF
#MT_SET

#telemetry
#(enum) MT_STATE
#(lin) MT_SIGN
#(lin) MT_DUTY
#(lin) MT_CURR
#(lin) MT_VOLT
#(lin) MT_TEMP
#(lin) MT_MAGMOM

@PROCESS('mt.model', NORMAL,
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
                                 'n', 'A', 'C',
                                 'T'),
              ins=(mt), reqs=('s',),
              outs=(), pros=('m', 'T', 'tau_bar')),
         Item('sc',
              evs=(), args=(),
              ins=(), reqs=('B_bar',),
              outs=(), pros=()))
def model(env, rail, wire, mt, sc):
    """Magnetorquer model"""
    (t0,) = env.next()
    (v,) = rail.next()
    (i,) = wire.next()
    (_hat, n, A, C, T) = mt.next()
    
    right = yield
    while True:
        env, rail, wire, mt, sc = (right['env'],
                                   right['rail'],
                                   right['wire'],
                                   right['mt'],
                                   right['sc'])
        (t,), _ = env.next()
        
        T += C * i * v * (t - t0)
        
        (v,), _ = rail.next()
        (i,), _ = wire.next()
        (s,), _ = mt.next()
        (B_bar,), _ = sc.next()
        
        m = s * (n * A) * i
        m_bar = m * _hat
        tau_bar = numpy.cross(m_bar, B_bar)
        t0 = t
        
        mt = (((m, T, tau_bar), ()),)
        left = {'mt': mt}
        right = yield left

@PROCESS('rw.sensor', NORMAL,
         Item('mt',
              evs=(), args=('_hat',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sc',
              evs=(), args=(),
              ins=(), reqs=('OM_bar', 'B_bar'),
              outs=(), pros=()),
         Item('obsr',
              evs=(True,), args=(),
              ins=(), reqs=(),
              outs=(), pros=('B_dot',)))
def sensor(mt, sc, obsr):
    """Magnetorquer sensor"""
    (_hat,) = mt.next()
    
    right = yield
    while True:
        sc = right['sc']
        (OM_bar, B_bar), _ = sc.next()

        B_dot = numpy.dot(numpy.cross(OM_bar, B_bar), _hat)
        
        obsr = (((B_dot,), ()),)
        left = {'obsr': obsr}
        right = yield left

@PROCESS('mt.actor', NORMAL,
         Item('rail',
              evs=(), args=(),
              ins=(), reqs=('v',),
              outs=(), pros=()),
         Item('wire',
              evs=(), args=('R',),
              ins=(), reqs=(),
              outs=(), pros=('i',)),
         Item('mt',
              evs=(), args=('n', 'A'),
              ins=(), reqs=(),
              outs=(), pros=('s', 'd')),
         Item('obsr',
              evs=(), args=(),
              ins=(), reqs=('B_dot',),
              outs=(), pros=()),
         Item('sc',
              evs=(True,), args=(),
              ins=(), reqs=('m',),
              outs=(), pros=()))
def actor(rail, wire, mt, obsr, ctlr):
    """Magnetorquer actor"""
    (n, A) = mt.next()
    (R,) = wire.next()
    
    right = yield
    while True:
        rail, obsr, ctlr = (right['rail'],
                            right['obsr'],
                            right['ctlr'])
        (v,), _ = rail.next()
        (B_dot,), _ = obsr.next()
        (m_,), _ = ctlr.next()

        u = (R / v) * m_ / (n * A)
        d = abs(u)#duty cycle
        s = int(u / d)#switch sign

        i = (d * v - s * n * A * B_dot) / R
        
        wire = (((i,), ()),)
        rw = (((s, d,), ()),)
        left = {'wire': wire,
                'mt': mt}
        right = yield left
