#built-in libraries
import math

#external libraries
import numpy

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('model',)

#constants
#...

#commands
#...

#telemetry
#...

@PROCESS('lum.model', NORMAL,
         Item('sun',
              evs=(), args=(),
              ins=(), reqs=('_hat',),
              outs=(), pros=()),
         Item('orb',
              evs=(), args=(),
              ins=(), reqs=('lum',),
              outs=(), pros=()),
         Item('area',
              evs=(), args=(),
              ins=(), reqs=('_hat',),
              outs=(), pros=('lum',)))
def model(env, sc, area):
    """Illumination model"""
    right = yield
    while True:
        sun, orb, area = (right['sun'],
                          right['orb'],
                          right['area'])
        (sol,), _ = sun.next()
        (lum,), _ = orb.next()
        if lum is True:
            area = (math.acos(numpy.dot(_hat, sol))
                    for ((_hat,), _) in area))
            area = (((th_i if th_i < math.pi else None,), ())
                    for th_i in area))
            left = {'area': area}
        else:
            left = {}
        right = yield left
