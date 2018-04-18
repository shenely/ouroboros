#include <math.h>
#include "geoid.h"

double tol = 1.48e-8;
int settol(double x) {
    tol = x;
    return 0;
}

int maxiter = 50;
int setmaxiter(int x) {
    maxiter = x;
    return 0;
}

double rad_e, e__2, fn1__2;
int setshape(double R, double f) {
    rad_e = R;
    e__2 = (2.0 - f) * f;
    fn1__2 = 1.0 - e__2;
    return 0;
}

int center2datum(double lat_c, double rad_c,
                 double* lat_d, double* alt_d) {
    *lat_d = lat_c;
    *alt_d = rad_c - rad_e;
    
    double r_cos_c = rad_c * cos(lat_c),
           r_sin_c = rad_c * sin(lat_c);
    
    double cos_d, sin_d, d;
    double rad_cos, rad_sin;
    double g, g_diff_lat, g_diff_alt;
    double h, h_diff_lat, h_diff_alt;
    double det, delta_lat, delta_alt;
    
    int i;
    for (i = 0; i < maxiter; i++) {
        cos_d = cos(*lat_d);
        sin_d = sin(*lat_d);
        d = 1.0 - e__2 * sin_d * sin_d;
        rad_cos = rad_e / sqrt(d);
        rad_sin = rad_cos * fn1__2;
        
        g = (rad_cos + (*alt_d)) * cos_d - r_cos_c;
        h = (rad_sin + (*alt_d)) * sin_d - r_sin_c;
        g_diff_lat = 0.5 * rad_cos * e__2 * cos_d * cos_d / d
                   - (rad_cos + (*alt_d)) * sin_d;
        h_diff_lat = 0.5 * rad_sin * e__2 * cos_d * sin_d / d
                   + (rad_sin + (*alt_d)) * cos_d;
        g_diff_alt = cos_d;
        h_diff_alt = sin_d;
        
        det = g_diff_lat * h_diff_alt - g_diff_alt * h_diff_lat;
        delta_lat = (g * h_diff_alt - h * g_diff_lat) / det;
        delta_alt = (h * g_diff_lat - g * h_diff_alt) / det;
        if ((fabs(delta_lat) < tol) &&
            (fabs(delta_alt) < tol)) {
            break;
        } else {
            *lat_d -= delta_lat;
            *alt_d -= delta_alt;
        }
    }
    if (i == maxiter) return 1;
    
    return 0;
}

int datum2center(double lat_d, double alt_d,
                 double* lat_c, double* rad_c) {
    double cos_d = cos(lat_d),
           sin_d = sin(lat_d);
    double sqrt_d = sqrt(1.0 - e__2 * sin_d * sin_d);
    double rad_cos = (rad_e          / sqrt_d + alt_d) * cos_d,
           rad_sin = (rad_e * fn1__2 / sqrt_d + alt_d) * sin_d;
                 
    *lat_c = atan2(rad_sin, rad_cos);
    *rad_c = sqrt(rad_cos * rad_cos +
                  rad_sin * rad_sin);
    
    return 0;
}
