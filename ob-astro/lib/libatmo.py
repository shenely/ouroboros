import math

STD_GRAVITY = 9.81  # m/s2
STD_PRESSURE = 101.325e3  # Pa
GAS_CONST = 8.31432  # J/K/mol
DRY_AIR = 28.9644e-3  # kg/mol

layers = ((0, 288.15, -0.0065),
          (11000, 216.65, 0.0),
          (20000, 216.65, 0.001),
          (32000, 228.65, 0.0028),
          (47000, 270.65, 0.0),
          (51000, 270.65, -0.0028),
          (71000, 214.65, -0.002))


def std_atmo(h, f10p7=0.0):
    g = STD_GRAVITY
    R = GAS_CONST / DRY_AIR
    p = STD_PRESSURE
    for base, pause in zip(layers[:-1], layers[1:]):
        h_base, T_base, T_grad = base
        h_pause,T_pause, _ = pause

        if h_base <= h < h_pause:
            T = T_base + T_grad * (h - h_base)
            if T_grad != 0.0:
                p *= (T / T_base) ** (- g / R / T_grad)
            else:
                p *= math.exp(- g / GAS_CONST * (h - h_base) / T_grad)
            break
        
        if T_grad != 0.0:
            p *= (T_pause / T_base) ** (- g / R / T_grad)
        else:
            p *= math.exp(- g / R * (h_pause - h_base) / T_base)
    else:
        h0, T0 = 120e3, 355
        T_inf = 500 + 3.4 * f10p7
        s = math.log((T_inf - T0) / (T_inf - T_pause)) / (h_pause - h0)
        T = T_inf - (T_inf - T0) * math.exp(- s * (h - h0))
        p *= math.exp(- (g / R) * (math.log(T / T_pause) +
                                   s * (h - h_pause)) / s / T_inf)

    rho = p / R / T
    return rho, p, T
