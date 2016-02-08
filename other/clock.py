from core import Process

__all__= ["clock"]

@Process((["t", "t_dt", "dt_td"],
          ["+1*"], ["clock"],
          ["t"], ["t_dt"]))
def clock(t,t_dt,dt_td):
    """Clock
    
    Arguments:
    - Start tick
    - Start date/time
    - Time step
    
    Inputs:
    - Every 1 tick
    
    Outputs:
    - Clock
    
    Requires:
    - Current tick
    
    Provides:
    - Current date/time
    """
    t0 = t
    
    while True:
        t, = yield t_dt,
        
        t_dt += dt_td * (t - t0)
        
        t0 = t
        
        print t_dt