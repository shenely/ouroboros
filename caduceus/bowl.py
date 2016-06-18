from math import sqrt

from numpy import array,concatenate,hstack,hsplit
from scipy.integrate import ode

def bowl(t0,r0_bar,v0_bar,
         mu,C_rr,R,R_max,
         mu_earth,R_earth):
    
    def gravity(t,y): 
        r = sqrt(y[0] ** 2 + y[1] ** 2)
        cos_ph = y[0] / r
        sin_ph = y[1] / r
        
        v = sqrt(y[2] ** 2 + y[3] ** 2)
        cos_ps = y[2] / v
        sin_ps = y[3] / v
        
        sin_th = 0 \
                 if r > R_max else \
                 (mu / mu_earth) * (R_earth / R) ** 2 * (r / R) \
                 if r < R else \
                 (mu / mu_earth) * (R_earth / r) ** 2
        cos_th = sqrt(1 - sin_th ** 2)
        
        g = mu_earth / R_earth ** 2
        a = -g * (sin_th * array([cos_ph,sin_ph]) + \
                  C_rr * cos_th * array([cos_ps,sin_ps]))
                  
        dy = concatenate((y[2:],a))
        
        return dy
    
    y = hstack((r0_bar,v0_bar))
    
    box = ode(gravity)\
            .set_integrator("dopri5") \
            .set_initial_value(y,t0)
    
    r_bar,v_bar = r0_bar,v0_bar
    
    while True:
        #Input/output
        t, = yield r_bar,v_bar#time/position,velocity
        
        #Update state
        y = box.integrate(t - t0)
        r_bar,v_bar = hsplit(y,2)