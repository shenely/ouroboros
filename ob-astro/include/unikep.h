#ifndef LIBUNIKEP_H
#define LIBUNIKEP_H

int settol(double);
int setmaxiter(int);
int setmu(double);

int stumpff(double, double*, double*);
int unikep(double*, double*,
           double*, double*,
           double);

#endif
