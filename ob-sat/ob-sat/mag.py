@Process("mag.model",
         ([], ["tick"], {}, [], []),#system
         ([], [], {}, ["_bar"], []),#B-field
         (["dt_td", "A"], [], {}, ["v_in", "_bar"], ["i_out"]))#mag
def model(A):
    """Magnetometer model"""
    dt = dt_td.total_seconds()

    n = arange(8)
    v_sense = zeros_like(n)
    while True:
        B_bar, v_drive, _bar, = yield i_sense,
        
        B = dot(B_bar, _bar)
        
        i_drive += (v_drive / L) * dt
        i_sense = A * B + i_drive
        
        