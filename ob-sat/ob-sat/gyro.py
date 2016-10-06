@Process("gyro.model",
         ([], ["tick"], {}, [], []),#system
         ([], [], {}, ["_t_bar"], []),#spin vector
         (["C"], [], {}, ["v_in", "_bar"], ["i_out"]))#gyro
def model(C):
    """Gyroscope"""
    v0_sense = 0

    n = arange(8)
    v_sense = zeros_like(n)
    while True:
        #[0|1|2|3|4|5|6|7]
        OM_bar, v_drive, _bar, = yield i_sense,
        
        OM = dot(OM_bar, _bar)
        
        i_sense = OM * C * v_drive
        
        