@Process("mt.model",
         ([], ["tick"], {}, [], []),#system
         (["A", "B"], [], {}, ["mu", "v_in"], ["mu"]))#mt
def model(A, B):
    """Magnetic torquer"""
    n = arange(8)
    while True:
        mu, v_drive, = yield mu,
        
        mu += A * (exp(B) - 1) * v_drive * exp(A)
        mu *= exp(- B)