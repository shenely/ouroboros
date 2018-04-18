#ifndef LIBGEOID_H
#define LIBGEOID_H

int settol(double);
int setmaxiter(int);
int setshape(double, double);

int center2datum(double, double,
                 double*, double*);

int datum2center(double, double,
                 double*, double*);

#endif
