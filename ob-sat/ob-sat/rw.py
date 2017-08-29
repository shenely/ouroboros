#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('power',)

#constants
#...

@PROCESS('rw.model', NORMAL,
         Item('power',
              evs=(), args=(),
              ins=(), reqs=('v_in',),
              outs=(), pros=('i_out',)),
         Item('data',
              evs=(), args=(),
              ins=(), reqs=('s1_in', 's2_in', 's3_in'),
              outs=(), pros=('V', 'C', 'T')),
         Item('dyno',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=(), pros=('L_bar',)),
         Item('rw',
              evs=(), args=('R', 'L', 'I'),
              ins=(), reqs=(),
              outs=(), pros=('rpm')))
@Process("rw.power",
         ([], ["tick"], {}, [], []),#system
         (["dt_td", "R", "L"], [], {}, ["v_in", "i_draw"], ["i_in"]))#rw
def power(dt_td, A, B):
    """Reaction wheel power"""
    dt = dt_td.total_seconds()
    
    while True:
        v, i, = yield i,
        
        i += (exp(R * dt / L) - 1) * v / R
        i *= exp(- R * dt / L)

@Process("rw.model",
         ([], ["tick"], {}, [], []),#system
         (["dt_td", "A", "B"], [], {}, ["om", "v_in"], ["om"]))#rw
def model(dt_td, A, B):
    """Reaction wheel model"""
    dt = dt_td.total_seconds()
    
    while True:
        #[0|1|2|3|4|5|6|7]
        om, v_drive, = yield om,
        
        om += A * (exp(B * dt) - 1) * v_drive
        om *= exp(- B * dt)
        
        
