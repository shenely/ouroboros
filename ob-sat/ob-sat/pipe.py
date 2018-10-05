#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('model',)

#constants
GAS_CONST = 8.314598#J/mol/K
AVOGADRO_CONST = 6.022140857e23#1/mol
BOLTZMANN_CONST = GAS_CONST / AVOGADRO_CONST#J/K

#commands
#...

#telemetry
#(lin) PIPE_TEMP

@PROCESS('pipe.model', NORMAL,
         Item('env',
              evs=(), args=('t',),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('one',
              evs=(), args=('C', 'A', 'T'),
              ins=(), reqs=('T',),
              outs=(), pros=('T',)),
         Item('two',
              evs=(), args=('C', 'A', 'T'),
              ins=(), reqs=('T',),
              outs=(), pros=('T',)),
         Item('pipe',
              evs=(True,), args=('C', 'L', 'T'),
              ins=(), reqs=('T',),
              outs=(), pros=('T',)))
def model(env, one, two, pipe):
    """Heat pipe model"""
    (t0,) = env.next()
    (C1, A1, T1) = one.next()
    (C2, A2, T2) = two.next()
    (C, L, T) = pipe.next()
    k = BOLTZMANN_CONST
    
    right = yield
    while True:
        dQ1 = - 2 * k * (A1 / L) * (T1 - T)
        dQ2 = - 2 * k * (A2 / L) * (T2 - T)
        dQ = 2 * k * (1 / L) * (A1 * T1 + A2 * T2 - (A1 + A2) * T)
        
        env, one, two, pipe = (right['env'],
                               right['one'],
                               right['two'],
                               right['pipe'])
        (t,), _ = env.next()
        (T1,), _ = one.next()
        (T2,), _ = two.next()
        (T,), _ = pipe.next()

        T1 += C1 * dQ1 * (t - t0)
        T2 += C2 * dQ2 (t - t0)
        T += C * dQ * (t - t0)
        t0 = t
        
        one = (((T1,), ()),)
        two = (((T2,), ()),)
        pipe = (((T,), ()),)
        left = {'one': one,
                'two': two,
                'pipe': pipe}
        right = yield left
