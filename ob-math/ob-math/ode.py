# built-in libraries
# ...

# external libraries
# ...

# internal libraries
from ouroboros import Image, Node

# exports
__all__= ("euler", "heun", "rk4")


@Image("ode.euler",
       env=Node(evs=(True,), args=("t",),
                ins=(True,), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("y",),
                outs=(True,), pros=("y",)),
       fun=Node(evs=("o",), args=(),
                ins=(), reqs=("f",),
                outs=("i",), pros=("t", "y")),
       usr=Node(evs=(True, False), args=("h",),
                ins=(True,), reqs=(),
                outs=(True,), pros=()))
def euler(env, sys, fun, usr):
    """(Forward) Euler method"""
    env_t0, = next(env.data)
    usr_h, = next(usr.data)
    
    evs = yield
    while True:
        env_t, = next(env.data)
        env_e, = next(env.ctrl)
        sys_y, = next(sys.data)
        usr_e, = next(usr.ctrl)
        
        env_h = env_t - env_t0
        env_t0 = env_t

        # k = f(t[n], y[n])
        fun.data.send((env_t, sys_y))
        yield (fun.ctrl.send((True,)),)
        fun_k, = next(fun.data)

        # y[n+1] = y[n] + h * k
        sys.data.send((sys_y + fun_k * env_h,))
        
        yield (sys.ctrl.send((True,)),
               usr.ctrl.send((env_t + usr_h,)
                             if env_e in evs
                             or usr_e in evs
                             else None))


@Image("ode.heun",
       env=Node(evs=(True,), args=("t",),
                ins=(True,), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("y",),
                outs=(True,), pros=("y",)),
       fun=Node(evs=("o",), args=(),
                ins=(), reqs=("f",),
                outs=("i",), pros=("t", "y")),
       usr=Node(evs=(True, False), args=("h",),
                ins=(True,), reqs=(),
                outs=(True,), pros=()))
def heun(env, sys, fun, usr):
    """Heun"s method"""
    env_t0, = next(env.data)
    usr_h, = next(usr.data)
    
    evs = yield
    while True:
        env_t, = next(env.data)
        env_e, = next(env.ctrl)
        sys_y, = next(sys.data)
        usr_e, = next(usr.ctrl)
        
        env_h = env_t - env_t0
        env_t0 = env_t

        # k[1] = f(t[n], y[n])
        fun.data.send((env_t, sys_y))
        yield (fun.ctrl.send((False,)),)
        fun_k1, = next(fun.data)

        # k[2] = f(t[n] + h, y[n] + h * k[1])
        fun.data.send((env_t + env_h,
                       sys_y + fun_k1 * env_h))
        yield (fun.ctrl.send((True,)),)
        fun_k2, = next(fun.data)

        # y[n+1] = y[n] + (h / 2) * (k[1] + k[2])
        sys.data.send((sys_y + (fun_k1 + fun_k2) * env_h / 2,))
        
        yield (sys.ctrl.send((True,)),
               usr.ctrl.send((env_t + usr_h,)
                             if env_e in evs
                             or usr_e in evs
                             else None))


@Image("ode.rk4",
       env=Node(evs=(True,), args=("t",),
                ins=(True,), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(), args=(),
                ins=(), reqs=("y",),
                outs=(True,), pros=("y",)),
       fun=Node(evs=("o",), args=(),
                ins=(), reqs=("f",),
                outs=("i",), pros=("t", "y")),
       usr=Node(evs=(True, False), args=("h",),
                ins=(True,), reqs=(),
                outs=(True,), pros=()))
def rk4(env, sys, fun, usr):
    """The Runge-Kutta method"""
    env_t0, = next(env.data)
    usr_h, = next(usr.data)
    
    evs = yield
    while True:
        env_t, = next(env.data)
        env_e, = next(env.ctrl)
        sys_y, = next(sys.data)
        usr_e, = next(usr.ctrl)
        
        env_h = env_t - env_t0
        env_t0 = env_t

        # k[1] = f(t[n], y[n])
        fun.data.send((env_t, sys_y))
        yield (fun.ctrl.send((False,)),)
        fun_k1, = next(fun.data)

        # k[2] = f(t[n] + h / 2, y[n] + h * k[1] / 2)
        fun.data.send((env_t + env_h / 2,
                       sys_y + fun_k1 * env_h / 2))
        yield (fun.ctrl.send((True,)),)
        fun_k2, = next(fun.data)

        # k[3] = f(t[n] + h / 2, y[n] + h * k[2] / 2)
        fun.data.send((env_t + env_h / 2,sys_y + fun_k2 * env_h / 2))
        yield (fun.ctrl.send((True,)),)
        fun_k3, = next(fun.data)

        # k[4] = f(t[n] + h, y[n] + h * k[3])
        fun.data.send((env_t + env_h,
                       sys_y + fun_k3 * env_h))
        yield (fun.ctrl.send((True,)),)
        fun_k4, = next(fun.data)

        # y[n+1] = y[n] + (h / 6) * (k[1] + 2 * k[2] + 2 * k[3] + k[4])
        sys.data.send((sys_y + env_j * (fun_k1
                                        + 2 * (fun_k2 + fun_k3)
                                        + fun_k4) / 6,)) 
        yield (sys.ctrl.send((True,)),
               usr.ctrl.send((env_t + usr_h,)
                             if env_e in evs
                             or usr_e in evs
                             else None))
