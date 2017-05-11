@Process("heat.pipe",
         (["dt_td", "k", "A", "L"], ["tock"], {}, [], []),#pipe
         ([], [], {}, ["U", "T"], ["U"]),#source
         ([], [], {}, ["U", "T"], ["U"]))#sink
def pipe(dt_td, k, A, L):
    """Heat pipe"""
    dt = dt_td.total_seconds()

    U1, U2 = 0, 0
    while True:
        U1, T1, U2, T2 = yield U1, U2,
        
        Q = k * A * L * (T1 - T2) / dt
        U1 -= Q
        U2 += Q
       
@Process("heat.panel",
         (["sigma"], [], [], [], [], []),#constants
         (["dt_td", "A"], [], {}, ["U", "T"], ["U"]))#panel
def panel(sigma, dt_td, A):
    """Radiator panel"""
    dt = dt_td.total_seconds()

    U = 0
    while True:
        U, T, = yield U,
        
        Q = sigma * A * T ** 4 / dt
        U -= Q