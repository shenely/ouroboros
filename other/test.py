from math import sqrt, cos, sin, degrees, radians

from numpy import array
from scipy.optimize import root

def sph2geo(R_km, f, r, el):    
    cos_el = cos(el)
    sin_el = sin(el)
    
    def fun(x):
        lat, alt = x
        
        return array([(R_km / sqrt(1 - (2 - f) * f * sin(lat) ** 2) +\
                       alt) * cos(lat) - r * cos_el,
                      ((1 - f) ** 2 * R_km / sqrt(1 - (2 - f) * f * sin(lat) ** 2) +\
                       alt) * sin(lat) - r * sin_el])
        
    def jac(x):
        lat, alt = x
        
        return array([[- (2 - f) * f * cos(lat) * sin(lat) *\
                       R_km /\
                       sqrt(1 - (2 - f) * f * sin(lat) ** 2) ** 3 -\
                       (R_km / sqrt(1 - (2 - f) * f * sin(lat) ** 2) +\
                        alt) * sin(lat),
                       cos(lat)],
                      [- (1 - f) ** 2 *\
                       (2 - f) * f * cos(lat) * sin(lat) *\
                       R_km /\
                       sqrt(1 - (2 - f) * f * sin(lat) ** 2) ** 3 +\
                       ((1 - f) ** 2 * R_km / sqrt(1 - (2 - f) * f * sin(lat) ** 2) +\
                        alt) * cos(lat),
                       sin(lat)]])
        
    x = array([el, r - R_km])
    
    lat_rad, alt_km = root(fun, x, jac=jac).x
        
    return alt_km, degrees(lat_rad)
    
R_km = 6378.137
f = 1 / 298.257223563
print sph2geo(R_km, f, 7000.0, radians(90))