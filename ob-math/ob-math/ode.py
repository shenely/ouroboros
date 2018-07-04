#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__= ('euler', 'heun', 'rk4',
          'exp')

@PROCESS('ode.euler', NORMAL,
         Item('env',
              evs=(True,), args=('t',),
              ins=(True,), reqs=('t',),
              outs=(), pros=()),
         Item('sys',
              evs=(), args=(),
              ins=(), reqs=('y',),
              outs=('ode',), pros=('y',)),
         Item('fun',
              evs=('o',), args=(),
              ins=(), reqs=('f',),
              outs=('i',), pros=('t', 'y')),
         Item('usr',
              evs=(True, False), args=('h',),
              ins=(True,), reqs=(),
              outs=(True,), pros=()))
def euler(env, sys, fun, usr):
    """(Forward) Euler method"""
    env_t0, = env.next()
    usr_h, = usr.next()
    
    right = yield
    while True:
        env, sys, usr = (right['env'],
                         right['sys'],
                         right['usr'])
        (env_t,), (env_e,) = env.next()
        (sys_y,), _ = sys.next()
        _, (usr_e,) = usr.next()
        env_h = env_t - env_t0
        env_t0 = env_t
        
        usr = (((), (env_t + usr_h,))
               if env_e is True
               or usr_e is True
               else (None, None),)

        #k = f(t[n], y[n])
        fun = (((env_t, sys_y), (True,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k,), _ = fun.next()

        #y[n+1] = y[n] + h * k
        sys = (((sys_y + fun_k * env_h,), (True,)),)
        
        left = {'sys': sys,
                'usr': usr}
        right = yield left

@PROCESS('ode.heun', NORMAL,
         Item('env',
              evs=(True,), args=('t',),
              ins=(True,), reqs=('t',),
              outs=(), pros=()),
         Item('sys',
              evs=(), args=(),
              ins=(), reqs=('y',),
              outs=('ode',), pros=('y',)),
         Item('fun',
              evs=('o',), args=(),
              ins=(), reqs=('f',),
              outs=('i',), pros=('t', 'y')),
         Item('usr',
              evs=(True, False), args=('h',),
              ins=(True,), reqs=(),
              outs=(True,), pros=()))
def heun(env, sys, fun, usr):
    """Heun's method"""
    env_t0, = env.next()
    usr_h, = usr.next()
    
    right = yield
    while True:
        env, sys, usr = (right['env'],
                         right['sys'],
                         right['usr'])
        (env_t,), (env_e,) = env.next()
        (sys_y,), _ = sys.next()
        _, (usr_e,) = usr.next()
        env_h = env_t - env_t0
        env_t0 = env_t
        
        usr = (((), (env_t + usr_h,))
               if env_e is True
               or usr_e is True
               else (None, None),)

        #k[1] = f(t[n], y[n])
        fun = (((env_t, sys_y), (False,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k1,), _ = fun.next()

        #k[2] = f(t[n] + h, y[n] + h * k[1])
        fun = (((env_t + env_h,
                 sys_y + fun_k1 * env_h),
                (True,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k2,), _ = fun.next()

        #y[n+1] = y[n] + (h / 2) * (k[1] + k[2])
        sys = (((sys_y + (fun_k1 + fun_k2) * env_h / 2,),
                (True,)),)

        left = {'sys': sys,
                'usr': usr}
        right = yield left

@PROCESS('ode.rk4', NORMAL,
         Item('env',
              evs=(True,), args=('t',),
              ins=(True,), reqs=('t',),
              outs=(), pros=()),
         Item('sys',
              evs=(), args=(),
              ins=(), reqs=('y',),
              outs=('ode',), pros=('y',)),
         Item('fun',
              evs=('o',), args=(),
              ins=(), reqs=('f',),
              outs=('i',), pros=('t', 'y')),
         Item('usr',
              evs=(True, False), args=('h',),
              ins=(True,), reqs=(),
              outs=(True,), pros=()))
def rk4(env, sys, fun, usr):
    """The Runge-Kutta method"""
    env_t0, = env.next()
    usr_h, = usr.next()
    
    right = yield
    while True:
        env, sys, usr = (right['env'],
                         right['sys'],
                         right['usr'])
        (env_t,), (env_e,) = env.next()
        (sys_y,), _ = sys.next()
        _, (usr_e,) = usr.next()
        env_h = env_t - env_t0
        env_t0 = env_t
        
        usr = (((), (env_t + usr_h,))
               if env_e is True
               or usr_e is True
               else (None, None),)

        #k[1] = f(t[n], y[n])
        fun = (((env_t, sys_y), (False,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k1,), _ = fun.next()

        #k[2] = f(t[n] + h / 2, y[n] + h * k[1] / 2)
        fun = (((env_t + env_h / 2,
                 sys_y + fun_k1 * (env_h / 2)),
                (False,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k2,), _ = fun.next()

        #k[3] = f(t[n] + h / 2, y[n] + h * k[2] / 2)
        fun = (((env_t + env_h / 2,
                 sys_y + fun_k2 * (env_h / 2)),
                (False,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k3,), _ = fun.next()

        #k[4] = f(t[n] + h, y[n] + h * k[3])
        fun = (((env_t + env_h,
                 sys_y + fun_k3 * env_h),
                (True,)),)
        left = {'fun': fun}
        right = yield left
        fun = right['fun']
        (fun_k4,), _ = fun.next()

        #y[n+1] = y[n] + (h / 6) * (k[1] + 2 * k[2] + 2 * k[3] + k[4])
        sys = (((sys_y + (fun_k1 +
                          (fun_k2 + fun_k3) * 2 +
                          fun_k4) * (env_h / 6),),
                (True,)),)

        left = {'sys': sys,
                'usr': usr}
        right = yield left

@PROCESS('ode.exp', NORMAL,
         Item('fun',
              evs=('i',), args=('k',),
              ins=(), reqs=('t', 'y'),
              outs=('o',), pros=('f',)))
def exp(fun):
    """Exponential growth"""
    k, = fun.next()

    right = yield
    while True:
        fun = right['fun']
        (t, y), _ = fun.next()
        y_dot = k * y
        fun = (((y_dot,), (False,)),)
        left = {'fun': fun}
        right = yield left
