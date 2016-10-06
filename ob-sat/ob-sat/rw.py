@Process("rw.model",
         ([], ["tick"], {}, [], []),#system
         (["A", "B"], [], {}, ["om", "v_in"], ["om"]))#rw
def model(A, B):
    """Reaction wheel"""
    n = arange(8)
    while True:
        #[0|1|2|3|4|5|6|7]
        om, v_drive, = yield om,
        
        om += (B / A) * (exp(A / 8) - 1) * sum(v_drive * exp(n * A / 8))
        om *= exp(-A)
        
        