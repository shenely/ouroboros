from core import Process

__all__= ["clock"]

@Process((["t", "t_dt", "dt_td"],
          ["+1*"], {"clock":True},
          ["t"], ["t_dt"]))
def clock(t,t_dt,dt_td):
    """Clock"""
    t0 = t
    
    while True:
        t, = yield t_dt,
        
        t_dt += dt_td * (t - t0)
        
        t0 = t
        
        print t_dt