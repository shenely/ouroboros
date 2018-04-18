#ifndef LIBORBELE_H
#define LIBORBELE_H

typedef struct ob_orbele_t {
    double sma;
    double mm;
    double ecc;
    double aop;
    double raan;
    double inc;
    double ta;
    double ea;
    double ma;
} ob_orbele;

int setmu(double);

int inv2law(double*, double*,
            double*, double*, double*);
int rec2kep(double*, double*,
            double, double*, double*,
            ob_orbele*);
int kep2rec(ob_orbele, double*, double*);

#endif
