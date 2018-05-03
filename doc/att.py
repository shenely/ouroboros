#built-in libraries
import math
import operator
import functools

#external libraries
import numpy
import numpy.random
import scipy.linalg

#internal libraries
import quat

#exports
__all__ = ()

#constants
O_BAR = numpy.zeros((3,), dtype=numpy.float64)

def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    return wrapper

@coroutine
def model(eye):
    inv_eye = scipy.linalg.inv(eye)
    
    t, y = yield
    while True:
        q, om = y
        q_dot = quat.mul(q, om / 2)
        om_dot =    - numpy.dot(inv_eye,
                                numpy.cross(om,
                                            numpy.dot(eye, om)))
        y_dot = q_dot, om_dot
        t, y = yield y_dot

def add(a, *b):
    return reduce(lambda x, y:
                  (quat.add(x[0], y[0]),
                   x[1] + y[1]), b, a)

def mul(a, b):
    return (quat.mul(a, b[0]), a * b[1])

@coroutine
def rk4(h, f,
        add=operator.__add__,
        mul=operator.__mul__):
    t, y = yield
    while True:
        k1 = f.send((t, y))
        k2 = f.send((t + h / 2, add(y, mul(h / 2, k1))))
        k3 = f.send((t + h / 2, add(y, mul(h / 2, k2))))
        k4 = f.send((t + h, add(y, mul(h, k3))))
        t += h
        y = add(y, mul(h / 6, add(k1, mul(2, k2), mul(2, k3), k4)))
        t, y = yield t, y

def main():
    samples = numpy.random.random_sample(12)
    
    #eye = numpy.diag(samples[0:3])
    eye = numpy.eye(3)
    f = model(eye)

    u, v, w = samples[3:6]
    q = (math.cos(math.pi * w),
         math.sin(math.pi * w) *
         numpy.array
         ([2 * v * math.sqrt(1 / v - 1) * math.cos(2 * math.pi * u),
           2 * v * math.sqrt(1 / v - 1) * math.sin(2 * math.pi * u),
           2 * v - 1]))
    u, v = samples[6:8]
    om_bar = (numpy.array
              ([2 * v * math.sqrt(1 / v - 1) * math.cos(2 * math.pi * u),
                2 * v * math.sqrt(1 / v - 1) * math.sin(2 * math.pi * u),
                2 * v - 1])) * (math.pi / 30)
    print q, om_bar
    
    h = 1.0
    quad = rk4(h, f, add=add, mul=mul)

    delta_t = 40.0
    u, v = samples[8:10]
    u_hat_b = (numpy.array
               ([2 * v * math.sqrt(1 / v - 1) * math.cos(2 * math.pi * u),
                 2 * v * math.sqrt(1 / v - 1) * math.sin(2 * math.pi * u),
                 2 * v - 1]))
    u, v = samples[10:12]
    v_hat_i = (numpy.array
               ([2 * v * math.sqrt(1 / v - 1) * math.cos(2 * math.pi * u),
                 2 * v * math.sqrt(1 / v - 1) * math.sin(2 * math.pi * u),
                 2 * v - 1]))
    print u_hat_b
    
    t = 0.0
    for i in xrange(61):
        #print t, om_bar

        _, v_hat_b = quat.rot(v_hat_i, q)
        u_dot_v = numpy.dot(u_hat_b, v_hat_b)
        u_cross_v = numpy.cross(u_hat_b, v_hat_b)
        #print t, v_hat_b, math.degrees(math.acos(u_dot_v))#, u_cross_v

        if True:
            print t, v_hat_b, math.degrees(math.acos(u_dot_v))
            om_bar = u_cross_v * (math.pi / 15)
        
        y = q, om_bar
        t, y = quad.send((t, y))
        q, om_bar = y
        q = quat.unit(q)
    
if __name__ == '__main__':
    main()
