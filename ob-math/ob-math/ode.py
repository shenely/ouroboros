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
        env_t, = env.reqs
        sys_t, sys_y = sys.reqs
        fun_h = env_t - sys_t

        # k = f(t[n], y[n])
        fun.pros = sys_t, sys_y
        yield (fun.outs((True,)),)
        fun_k, = fun.reqs

        # y[n+1] = y[n] + h * k
        sys.data = env_t, sys_y + fun_k * fun_h
        yield (sys.outs((True,)),)


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
        env_t, = env.reqs
        sys_t, sys_y = sys.reqs
        fun_h = env_t - sys_t

        # k[1] = f(t[n], y[n])
        fun.pros = sys_t, sys_y
        yield (fun.outs((False,)),)
        fun_k1, = fun.reqs

        # k[2] = f(t[n] + h, y[n] + h * k[1])
        fun.pros = (sys_t + fun_h,
                    sys_y + fun_k1 * fun_h)
        yield (fun.outs((True,)),)
        fun_k2, = fun.reqs

        # y[n+1] = y[n] + (h / 2) * (k[1] + k[2])
        sys.pros = env_t, sys_y + (fun_k1 + fun_k2) * env_h / 2
        yield (sys.outs((True,)),)


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
    while True:
        env_t, = env.reqs
        sys_t, sys_y = sys.reqs
        fun_h = env_t - sys_t

        # k[1] = f(t[n], y[n])
        fun.pros = sys_t, sys_y
        yield (fun.outs((False,)),)
        fun_k1, = fun.reqs

        # k[2] = f(t[n] + h / 2, y[n] + h * k[1] / 2)
        fun.pros = (sys_t + fun_h / 2,
                    sys_y + fun_k1 * (fun_h / 2))
        yield (fun.outs((False,)),)
        fun_k2, = fun.reqs

        # k[3] = f(t[n] + h / 2, y[n] + h * k[2] / 2)
        fun.pros = (sys_t + fun_h / 2,
                    sys_y + fun_k2 * (fun_h / 2))
        yield (fun.outs((False,)),)
        fun_k3, = fun.reqs

        # k[4] = f(t[n] + h, y[n] + h * k[3])
        fun.pros = (sys_t + fun_h,
                    sys_y + fun_k3 * fun_h)
        yield (fun.outs((True,)),)
        fun_k4, = fun.reqs

        # y[n+1] = y[n] + (h / 6) * (k[1] + 2 * k[2] + 2 * k[3] + k[4])
        sys.pros = (env_t, sys_y + (fun_k1
                                    + (fun_k2 + fun_k3) * 2
                                    + fun_k4) * (fun_h / 6))
        yield (sys.outs((True,)),)
