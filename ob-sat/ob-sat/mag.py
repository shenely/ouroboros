@Process("mag.model",
         ([], ["tick"], {}, [], []),#system
         ([], [], {}, ["_bar"], []),#B-field
         (["L", "A", "N"], [], {}, ["v_in", "_bar"], ["i_out"]))#mag
def model(L, A, N):
    """Magnetometer"""
    i0_drive = 0

    n = arange(8)
    v_sense = zeros_like(n)
    while True:
        #[0|1|2|3|4|5|6|7]
        B_bar, v_drive, _bar, = yield i_sense,
        
        B = dot(B_bar, _bar)
        
        i_drive = cumsum(v_drive) / 8 / L_mag + i0_drive
        i_sense = (A * N / L) * B + i_drive
        i0_drive = i_drive[-1]
        
        