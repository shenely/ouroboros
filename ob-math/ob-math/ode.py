# built-in libraries
# ...

# external libraries
# ...

# internal libraries
from ouroboros import Image, Node

# exports
__all__= ("euler", "heun", "rk4")


@Image(".ode@euler",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("t", "y"),
                outs=(True,), pros=("t", "y")),
       fun=Node(evs=(False,), args=(),
                ins=(), reqs=("f",),
                outs=(True,), pros=("t", "y")))
def euler(env, sys, fun):
    """(Forward) Euler method"""
    yield
    while True:
        env_t, = next(env.data)
        sys_t, sys_y = next(sys.data)
        fun_h = env_t - sys_t

        # k = f(t[n], y[n])
        fun.data.send((sys_t, sys_y))
        yield (fun.ctrl.send((True,)),)
        fun_k, = next(fun.data)

        # y[n+1] = y[n] + h * k
        sys.data.send((env_t, sys_y + fun_k * fun_h))
        yield (sys.ctrl.send((True,)),)


@Image(".ode@heun",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("t", "y"),
                outs=(True,), pros=("t", "y")),
       fun=Node(evs=(False,), args=(),
                ins=(), reqs=("f",),
                outs=(True,), pros=("t", "y")))
def heun(env, sys, fun):
    """Heun"s method"""
    yield
    while True:
        env_t, = next(env.data)
        sys_t, sys_y = next(sys.data)
        fun_h = env_t - sys_t

        # k[1] = f(t[n], y[n])
        fun.data.send((sys_t, sys_y))
        yield (fun.ctrl.send((False,)),)
        fun_k1, = next(fun.data)

        # k[2] = f(t[n] + h, y[n] + h * k[1])
        fun.data.send((sys_t + fun_h,
                       sys_y + fun_k1 * fun_h))
        yield (fun.ctrl.send((True,)),)
        fun_k2, = next(fun.data)

        # y[n+1] = y[n] + (h / 2) * (k[1] + k[2])
        sys.data.send((env_t, sys_y + (fun_k1 + fun_k2) * env_h / 2))
        yield (sys.ctrl.send((True,)),)


@Image(".ode@rk4",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("t", "y"),
                outs=(True,), pros=("t", "y")),
       fun=Node(evs=(False,), args=(),
                ins=(), reqs=("f",),
                outs=(True,), pros=("t", "y")))
def rk4(env, sys, fun):
    """The Runge-Kutta method"""
    yield
    next(fun.data)
    while True:
        env_t, = next(env.data)
        sys_t, sys_y = next(sys.data)
        fun_h = env_t - sys_t

        # k[1] = f(t[n], y[n])
        fun.data.send((sys_t, sys_y))
        yield (fun.ctrl.send((False,)),)
        fun_k1, = next(fun.data)

        # k[2] = f(t[n] + h / 2, y[n] + h * k[1] / 2)
        fun.data.send((sys_t + fun_h / 2,
                       sys_y + fun_k1 * (fun_h / 2)))
        yield (fun.ctrl.send((False,)),)
        fun_k2, = next(fun.data)

        # k[3] = f(t[n] + h / 2, y[n] + h * k[2] / 2)
        fun.data.send((sys_t + fun_h / 2,
                       sys_y + fun_k2 * (fun_h / 2)))
        yield (fun.ctrl.send((False,)),)
        fun_k3, = next(fun.data)

        # k[4] = f(t[n] + h, y[n] + h * k[3])
        fun.data.send((sys_t + fun_h,
                       sys_y + fun_k3 * fun_h))
        yield (fun.ctrl.send((True,)),)
        fun_k4, = next(fun.data)

        # y[n+1] = y[n] + (h / 6) * (k[1] + 2 * k[2] + 2 * k[3] + k[4])
        sys.data.send((env_t, sys_y + (fun_k1
                                       + (fun_k2 + fun_k3) * 2
                                       + fun_k4) * (fun_h / 6)))
        yield (sys.ctrl.send((True,)),)
