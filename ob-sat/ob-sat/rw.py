

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
        
        