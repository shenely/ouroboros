from math import pi,radians,degrees,sqrt,cos,sin,acos,asin,atan2
import functools

from numpy import array, cross, dot, matrix, hstack, hsplit
from scipy.linalg import norm
from scipy.integrate import ode

from core import Process

EARTH_RADIUS = 6378.1

#Unit vectors
O = array([0,0,0])
I = array([1,0,0])
J = array([0,1,0])
K = array([0,0,1])

TOP = matrix([[1,-1,-1,1],
              [1,1,-1,-1],
              [1,1,1,1]]) / sqrt(3)
                    
BOTTOM = matrix([[1,-1,-1,1],
                 [1,1,-1,-1],
                 [-1,-1,-1,-1]]) / sqrt(3)
                       
KILO = 1000

kepler_equ = lambda E,M,e:E - e * sin(E) - M
kepler_diff = lambda E,M,e:1 - e * cos(E)
                       
#Wrapper functions for angles in degrees
@functools.wraps(cos)
def cosd(x):return cos(radians(x))

@functools.wraps(sin)
def sind(x):return sin(radians(x))
    
@Process([(0,"t"),(0,"t_dt"),(0,"dt_td")],
         [(0,"+1*")],[(0,"clock")],
         [(0,"t")],[(0,"t_dt")])
def clock(t,t_dt,dt_td):
    t0 = t
    while True:
        t, = yield t_dt,
        
        t_dt += dt_td * (t - t0)
        
        t0 = t

@Process([],
         [(0,"+1*")],[(1,"earth")],
         [(0,"t_dt")],[(1,"th_G")])
def earth():
    th_G = 100.4606184
    
    while True:
        t_dt, = yield th_G,
        
        J0 = 367 * t_dt.year \
           - (7 * (t_dt.year + (t_dt.month + 9) / 12) / 4) \
           + 275 * t_dt.month / 9 \
           + t_dt.day + 1721013.5
        UT = t_dt.hour +\
             (t_dt.minute +\
              (t_dt.second +\
               t_dt.microsecond \
               / 1e6) \
              / 60) \
             / 60
        T0 = (J0 - 2451545) / 36525
        th_G0 = 100.4606184 \
              + (36000.77004 \
                 + (0.000387933 \
                    - 2.583e-8 \
                    * T0) \
                 * T0) \
              * T0
        th_G = th_G0 + 360.98564724 * UT / 24
        
        th_G %= 360
        
@Process([(2,"R_km"),(2,"f"),(2,"th_G"),(1,"lat_deg"),(1,"lon_deg"),(1,"alt_m")],
         [(0,"+5*")],[(1,"geo")],
         [(2,"th_G")],[(1,"r_bar")]) 
def geo(R_km,f,th_G,lat_deg,lon_deg,alt_m):
    alt_km = alt_m / KILO
    
    while True:
        th_deg = th_G + lon_deg
        
        R_ph = R_km / sqrt(1 - (2 * f - f ** 2) * sind(lat_deg) ** 2)
        R_cos = R_ph + alt_km
        R_sin = R_ph * (1 - f) ** 2 + alt_km
        
        r_bar = array([R_cos * cosd(lat_deg) * cosd(th_deg),
                       R_cos * cosd(lat_deg) * sind(th_deg),
                       R_sin * sind(lat_deg)])
        
        th_G, = yield r_bar,

@Process([],
         [(0,"+0")],[(1,"astro")],
         [(1,"ra_deg"),(1,"dec_deg")],[(1,"r_hat")])
def astro():
    ra_deg,dec_deg = yield
    
    r_hat = matrix([cosd(dec_deg) * cosd(ra_deg),
                    cosd(dec_deg) * sind(ra_deg),
                    sind(dec_deg)]).T
                    
    yield r_hat,

@Process([(0,"t_dt"),(1,"r_bar"),(1,"v_bar"),(2,"mu")],
         [(0,"+1*")],[(1,"orbit")],
         [(0,"t_dt"),],[(1,"r_bar"),(1,"v_bar")])
def orbit(t0_dt,r0_bar,v0_bar,mu):
    def gravity(mu):
        def gravity(t,y):
            r_bar,v_bar = hsplit(y,2)
            
            r = norm(r_bar)
            r_hat = r_bar / r
            
            a = mu / r ** 2
            a_bar = - a * r_hat
            
            dy = hstack((v_bar,a_bar))
            
            return dy
        return gravity
    
    y = hstack((r0_bar,v0_bar))
    
    box = ode(gravity(mu))\
            .set_integrator("dopri5") \
            .set_initial_value(y,0)
    
    r_bar,v_bar = r0_bar,v0_bar
    
    while True:
        #Input/output
        t_dt, = yield r_bar,v_bar#time/position,velocity
        
        #Update state
        y = box.integrate((t_dt - t0_dt).total_seconds())
        r_bar,v_bar = hsplit(y,2)

@Process([],
         [(0,"orbit")],[(0,"nrt2geo")],
         [(0,"r_bar")],[(0,"arc_km"),(0,"lat_deg"),(0,"lon_deg")])
def nrt2geo():
    arc_km = 0
    lat_deg = 0
    lon_deg = 0

    while True:
        r_bar, = yield arc_km, lat_deg, lon_deg,

        r = norm(r_bar)

        alpha_rad = atan2(r_bar[1],r_bar[0])
        delta_rad = asin(r_bar[2] / r)

        arc_km = degrees(acos(EARTH_RADIUS / r))
        lat_deg = degrees(delta_rad)
        lon_deg = degrees(alpha_rad)
        
@Process(["t","th_bar","om_bar"],
         ["+10*"],["attitude"],
         ["t","om_bar"],["x_hat","y_hat","z_hat"])
def attitude(t0,th_bar=O,om_bar=O):
    #Axis/angle
    th = norm(th_bar)#normal
    th_hat = th_bar / th if th != 0 else O#unit vector
    
    #Derived values
    cos_th = cos(th)
    sin_th = sin(th)
    
    #Principal axes
    x_hat = cos_th * I \
          + sin_th * cross(th_hat,I) \
          + (1 - cos_th) * th_hat[0,0] * th_hat#x
    y_hat = cos_th * J \
          + sin_th * cross(th_hat,J) \
          + (1 - cos_th) * th_hat[0,1] * th_hat#y
    z_hat = cos_th * K \
          + sin_th * cross(th_hat,K) \
          + (1 - cos_th) * th_hat[0,2] * th_hat#z
    
    while True:
        #Angular velocity
        om = norm(om_bar)#normal
        om_hat = om_bar / om if om != 0 else O#unit vector
        
        #Input/output
        t,om_bar = yield x_hat,y_hat,z_hat#time,om/x-,y-,z-axis
        
        #Angle change
        omt = om * (t - t0)
        cos_omt = cos(omt)
        sin_omt = sin(omt)
        
        #Update axes
        x_hat = cos_omt * x_hat \
              + sin_omt * cross(om_hat,x_hat) \
              + (1 - cos_omt) * dot(om_hat,x_hat) * om_hat
        y_hat = cos_omt * y_hat \
              + sin_omt * cross(om_hat,y_hat) \
              + (1 - cos_omt) * dot(om_hat,y_hat) * om_hat
        z_hat = cos_omt * z_hat \
              + sin_omt * cross(om_hat,z_hat) \
              + (1 - cos_omt) * dot(om_hat,z_hat) * om_hat
              
        #Update time
        t0 = t