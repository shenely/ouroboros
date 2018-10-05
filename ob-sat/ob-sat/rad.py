#built-in libraries
import math

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
PLANCK_CONST = 6.6260700403-34#J-s
SPEED_OF_LIGHT = 299792458.0#m/s
STEFAN_BOLTZMANN = (
    (2 * math.pi ** 5 / 15)
    * BOLTZMANN_CONST ** 4
    / LIGHT_SPEED ** 2
    / PLANCK_CONST ** 3
)#W-m2/K4

#commands
#...

#telemetry
#(lin) RAD_TEMP

@PROCESS('rad.model', NORMAL,
         Item('env',
              evs=(), args=('t',),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('rad',
              evs=(True,), args=('eps', 'A', 'T'),
              ins=(), reqs=('T',),
              outs=(), pros=('T',)))
def model(env, rad):
    """Radiator model"""
    (t0,) = env.next()
    (eps, A, T) = rad.next()
    sigma = STEFAN_BOLTZMANN
    
    right = yield
    while True:
        dQ = - eps * sigma * A * T ** 4
        
        env, rad = (right['env'],
                    right['rad'])
        (t,), _ = env.next()
        (T,), _ = rad.next()

        T += C * dQ * (t - t0)
        t0 = t
        
        rad = (((T,), ()),)
        left = {'rad': rad}
        right = yield left
