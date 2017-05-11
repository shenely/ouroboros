@Process("pdm.signal",
         ([], ["tick"], {}, [], []),#system
         (["t_dt", "V0"], [], {}, ["s_ctrl"], ["v_in"]))#mag
def signal(t_dt, V0):
    """Pulse-density modulation"""
    t = t_dt.total_seconds()
    
    v_drive = 0
    while True:
        s_ctrl, = yield v_drive,
        for n in range(32):
            v_drive =  (-V0) * (-1) ** (s_ctrl % 2)
            s_ctrl >>= 1
            
            yield v_drive,