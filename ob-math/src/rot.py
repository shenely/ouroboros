#built-in imports
from math import pi

#external imports
from numpy import dot, cross, hstack, hsplit
from scipy.linalg import inv, norm
from scipy.integrate import ode

#internal imports
from ouroboros import Item, PROCESS

#exports
__all__= ["model",
          "quat2rec", "rec2quat",
          "quat2rpy", "rpy2quat",
          "quat2mat", "mat2quat"]

#constants
KILO = 1000
MICRO = 1e-6

@Process("rot.model",
         (["t_dt"], ["+1*"], [], ["t_dt"], []),
         (["_bar", "_t_bar"], [], {"rec":True}, [], ["_bar", "_t_bar"]),
         (["_mat"], [], [], [], []))
def model(t0_dt, th0_bar, om0_bar, I_mat):
    I_inv = inv(I_mat)

    def rigid(t, y):
        th_bar, om_bar = hsplit(y, 2)
        
        dy = hstack((om_bar, - dot(I_inv, cross(om_bar, dot(I_mat, om_bar)))))
        
        return dy
    
    y = hstack((th0_bar, om0_bar))
    
    box = ode(rigid)\
            .set_integrator("dopri5") \
            .set_initial_value(y, 0)
    
    th_bar, om_bar = th0_bar, om0_bar
    
    while True:
        #Input/output
        t_dt, = yield th_bar, om_bar,#time/position,velocity
        
        #Update state
        y = box.integrate((t_dt - t0_dt).total_seconds())
        th_bar, om_bar = hsplit(y, 2)
        
        th = norm(th_bar)
        
        if 0 < abs(th) > 2 * pi:
            th_hat = th_bar / th
            th = th % (2 * pi)
            
            th_bar = th * th_hat

def quat2rec():pass
def rec2quat():pass
def quat2rpy():pass
def rpy2quat():pass
def quat2mat():pass
def mat2quat():pass
