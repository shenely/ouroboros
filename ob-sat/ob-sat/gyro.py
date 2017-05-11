@Process("gyro.model",
         ([], ["tick"], {}, [], []),#system
         ([], [], {}, ["_t_bar"], []),#spin vector
         (["A"], [], {}, ["v_in", "_bar"], ["i_out"]))#gyro
def model(A):
    """Gyroscope"""
    i_sense = 0
    while True:
        OM_bar, v_drive, _bar, = yield i_sense,
        
        OM = dot(OM_bar, _bar)
        
        i_sense = A * OM * v_drive
        
        