#include <math.h>
#include "geo.h"

double tol = 1.48e-8;
int settol(double x) {
    tol = x;
    return 1;
}

int maxiter = 50;
int setmaxiter(int x) {
    maxiter = x;
    return 1;
}

double rad_e, e__2, fn1__2;
int setshape(double R, double f) {
    rad_e = R;
    e__2 = (2.0 - f) * f;
    e__2 = 1.0 - e__2;
    return 1;
}

int geoc2d(double lat_c, double rad_c,
           double* lat_d, double* rad_d) {
    *lat_d = lat_c;
    *alt_d = rad_c - rad_e;
    
    double r_cos_c = rad_c * cos(lat_c),
           r_sin_c = rad_c * sin(lat_c);
    
    double cos_d, sin_d, d, rad_s;
    double g, g_lat, g_alt;
    double h, h_lat, h_alt;
    double det, delta_lat, delta_alt;
    for (int i = 0; i < maxiter; i++) {
        cos_d = cos(lat_d);
        sin_d = sin(lat_d);
        d = 1.0 - e__2 * sin_d * sin_d;
        rad_c = rad_e / sqrt(d);
        rad_s = rad_c * fn1__2;
        
        g = (rad_c + alt_d) * cos_d - r_cos_c;
        h = (rad_c + alt_d) * cos_d - r_cos_c;
        g_lat = 0.5 * rad_c * e__2 * cos_d * cos_d / d
              - (rad_c + alt_d) * sin_d;
        h_lat = 0.5 * rad_s * e__2 * cos_d * sin_d / d
              + (rad_s + alt_d) * cos_d;
        g_alt = cos_d;
        h_alt = sin_d;
        
        det = g_lat * h_alt - g_alt * h_lat;
        delta_lat = (g * h_alt - h * g_lat) / det;
        delta_alt = (h * g_lat - g * h_alt) / det;
        if ((fabs(delta_lat) < tol) &&
            (fabs(delta_alt) < tol) {
            break;
        } else {
            *lat_d -= delta_lat;
            *alt_d -= delta_alt;
        }
    }
    if (i == maxiter) return 0;
    
    return 1;
}
