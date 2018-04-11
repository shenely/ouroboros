#include <stdio.h>
#include <math.h>
#include "unikep.h"

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

double sqrt_mu;
int setmu(double x) {
    sqrt_mu = sqrt(x);
    return 0;
}

int stumpff(double z, double* C, double* S) {
    double sqrt_z = sqrt(fabs(z));
    if (z > 0.0) {
        *C = (1.0 - cos(sqrt_z)) / z;
        *S = (sqrt_z - sin(sqrt_z)) / z / sqrt_z;
    } else if (z < 0.0) {
        *C = (1.0 - cosh(sqrt_z)) / z;
        *S = (sqrt_z - sinh(sqrt_z)) / z / sqrt_z;
    } else {
        *C = 1.0 / 2.0;
        *S = 1.0 / 6.0;
    }
    return 0;
}

int unikep(double* r0_bar, double* v0_bar,
           double* r_bar,  double* v_bar,
           double t) {
    double r0 = sqrt(r0_bar[0] * r0_bar[0] + 
                     r0_bar[1] * r0_bar[1] +
                     r0_bar[2] * r0_bar[2]),
           v0 = sqrt(v0_bar[0] * v0_bar[0] + 
                     v0_bar[1] * v0_bar[1] +
                     v0_bar[2] * v0_bar[2]);
    double r0_dot_v0 = r0_bar[0] * v0_bar[0]
                     + r0_bar[1] * v0_bar[1]
                     + r0_bar[2] * v0_bar[2];
    double alpha = 2.0 / r0 - (v0 * v0) / (sqrt_mu * sqrt_mu);
    printf("r0 = %f, v0 = %f\n", r0, v0);
    printf("alpha = %e\n", alpha);
    
    double chi, chi__2, chi__3;
    chi = sqrt_mu * fabs(alpha) * t;
    
    double z, C, S;
    double F, Fprime, delta;
    
    int i;
    for (i = 0; i < maxiter; i++) {
        printf("i = %d, chi = %f\n", i, chi);
        chi__2 = chi * chi;
        chi__3 = chi * chi__2;
        z = alpha * chi__2;
        stumpff(z, &C, &S);
        F = r0_dot_v0 * chi__2 * C / sqrt_mu
          + (1.0 - alpha * r0) * chi__3 * S
          + r0 * chi - sqrt_mu * t;
        Fprime = r0_dot_v0 * chi * (1.0 - alpha * chi__2 * S) / sqrt_mu
               + (1.0 - alpha * r0) * chi__2 * C
               + r0;
        delta = F / Fprime;
        if (fabs(delta) < tol) {
            break;
        } else {
            chi -= delta;
        }
    }
    if (i == maxiter) return 0;
    
    double f = 1.0 - chi__2 * C / r0,
           g = t - chi__3 * S / sqrt_mu;
    printf("f = %f, g = %f\n", f, g);
    r_bar[0] = f * r0_bar[0] + g * v0_bar[0];
    r_bar[1] = f * r0_bar[1] + g * v0_bar[1];
    r_bar[2] = f * r0_bar[2] + g * v0_bar[2];
    double r = sqrt(r_bar[0] * r_bar[0] + 
                    r_bar[1] * r_bar[1] +
                    r_bar[2] * r_bar[2]);
    double f_dot = sqrt_mu * (alpha * chi__3 * S - chi) / (r * r0),
           g_dot = 1.0 - chi__2 * C / r;
    printf("f_dot = %f, g_dot = %f\n", f_dot, g_dot);
    v_bar[0] = f_dot * r0_bar[0] + g_dot * v0_bar[0];
    v_bar[1] = f_dot * r0_bar[1] + g_dot * v0_bar[1];
    v_bar[2] = f_dot * r0_bar[2] + g_dot * v0_bar[2];
    return 0;
}
