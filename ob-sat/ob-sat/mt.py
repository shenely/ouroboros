@Process("mt.model",
         ([], ["tick"], {}, [], []),#system
         (["R", "L", "A"], [], {}, ["mu", "v_in"], ["mu"]))#mt
def model(C):
    """Magnetic torquer"""
    n = arange(8)
    while True:
        #[0|1|2|3|4|5|6|7]
        mu, v_drive, = yield mu,
        
        mu += (A / R) * (exp((R / L) / 8) - 1) * sum(v_drive * exp(n * (R / L) / 8))
        mu *= exp(-R / L)