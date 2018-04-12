#include <math.h>
#include "orbele.h"

double mu;
int setmu(double x) {
    mu = x;
    return 0;
}

int inv2law(double* r_bar, double* v_bar,
            double* eps, double* h_bar, double* e_bar) {
    double r = sqrt(r_bar[0] * r_bar[0] +
                    r_bar[1] * r_bar[1] +
                    r_bar[2] * r_bar[2]);

    *eps = 0.5 * (v_bar[0] * v_bar[0] +
                  v_bar[1] * v_bar[1] +
                  v_bar[2] * v_bar[2]) - mu / r;
    h_bar[0] = r_bar[1] * v_bar[2] - r_bar[2] * v_bar[1];
    h_bar[1] = r_bar[2] * v_bar[0] - r_bar[0] * v_bar[2];
    h_bar[2] = r_bar[0] * v_bar[1] - r_bar[1] * v_bar[0];
    e_bar[0] = (v_bar[1] * h_bar[2] - v_bar[2] * h_bar[1]) / mu
             - r_bar[0] / r;
    e_bar[1] = (v_bar[2] * h_bar[0] - v_bar[0] * h_bar[2]) / mu
             - r_bar[1] / r;
    e_bar[2] = (v_bar[0] * h_bar[1] - v_bar[1] * h_bar[0]) / mu
             - r_bar[2] / r;
    return 0;
}

int rec2kep(double* r_bar, double* v_bar,
            double eps, double* h_bar, double* e_bar,
            ob_orbele* kep) {
    double r = sqrt(r_bar[0] * r_bar[0] +
                    r_bar[1] * r_bar[1] +
                    r_bar[2] * r_bar[2]),
           r_dot_v = r_bar[0] * v_bar[0]
                   + r_bar[1] * v_bar[1]
                   + r_bar[2] * v_bar[2],
           h = sqrt(h_bar[0] * h_bar[0] +
                    h_bar[1] * h_bar[1] +
                    h_bar[2] * h_bar[2]),
           e_dot_r = e_bar[0] * r_bar[0]
                   + e_bar[1] * r_bar[1]
                   + e_bar[2] * r_bar[2],
           n_dot_e = - h_bar[1] * e_bar[0]
                     + h_bar[0] * e_bar[1],
           n = sqrt(h_bar[0] * h_bar[0] +
                    h_bar[1] * h_bar[1]);

    (*kep).sma = - 0.5 * mu / eps;
    (*kep).mm = sqrt(- 8.0 * eps * eps * eps) / mu;
    (*kep).ecc = sqrt(e_bar[0] * e_bar[0] +
                      e_bar[1] * e_bar[1] +
                      e_bar[2] * e_bar[2]);
    (*kep).aop  = acos(n_dot_e / (n * (*kep).ecc));
    (*kep).raan = acos(- h_bar[1] / n);
    (*kep).inc  = acos(h_bar[2] / h);
    (*kep).ta   = acos(e_dot_r / ((*kep).ecc * r));
    
    if (e_bar[2] < 0.0) (*kep).aop  = 2.0 * M_PI - (*kep).aop;
    if (h_bar[0] < 0.0) (*kep).raan = 2.0 * M_PI - (*kep).raan;
    if (r_dot_v  < 0.0) (*kep).ta   = 2.0 * M_PI - (*kep).ta;
    
    (*kep).ea = 2.0 * atan2(sqrt(1.0 - (*kep).ecc) * sin(0.5 * (*kep).ta),
                            sqrt(1.0 + (*kep).ecc) * cos(0.5 * (*kep).ta));
    (*kep).ma = (*kep).ea - (*kep).ecc * sin((*kep).ea);
    return 0;
}

int kep2rec(ob_orbele kep,
            double* r_bar, double* v_bar) {
    double sam = sqrt(mu * kep.sma * (1.0 - kep.ecc));
    double cos_ta = cos(kep.ta),
           sin_ta = sin(kep.ta),
           cos_aop = cos(kep.aop),
           sin_aop = sin(kep.aop),
           cos_raan = cos(kep.raan),
           sin_raan = sin(kep.raan),
           cos_inc = cos(kep.inc),
           sin_inc = sin(kep.inc);
    double r = mu / sam,
           v_dot_th = sam * sam / mu / (1.0 + kep.ecc * cos_ta);
    double r_dot_p = r * cos_ta,
           r_dot_q = r * sin_ta,
           v_dot_p = - v_dot_th * sin_ta,
           v_dot_q =   v_dot_th * (kep.ecc + cos_ta);
    double p_dot_i =   cos_aop * cos_raan - sin_aop * sin_raan * cos_inc,
           p_dot_j =   cos_aop * sin_raan + sin_aop * cos_raan * cos_inc,
           p_dot_k =   sin_aop * sin_inc,
           q_dot_i = - sin_aop * cos_raan - cos_aop * sin_raan * cos_inc,
           q_dot_j = - sin_aop * sin_raan + cos_aop * cos_raan * cos_inc,
           q_dot_k =   cos_aop * sin_inc;
    
    r_bar[0] = r_dot_p * p_dot_i + r_dot_q * q_dot_i;
    r_bar[1] = r_dot_p * p_dot_j + r_dot_q * q_dot_j;
    r_bar[2] = r_dot_p * p_dot_k + r_dot_q * q_dot_k;
    v_bar[0] = v_dot_p * p_dot_i + v_dot_q * q_dot_i;
    v_bar[1] = v_dot_p * p_dot_j + v_dot_q * q_dot_j;
    v_bar[2] = v_dot_p * p_dot_k + v_dot_q * q_dot_k;
    return 1;
}

