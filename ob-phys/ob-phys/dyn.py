# built-in libraries
# ...

# external libraries
import numpy
import scipy.linalg

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.lib import libkin
from ouroboros.lib import libquat

# exports
__all__ = ("kin", "rot",
           "force", "torque",
           "lerp", "slerp")

kin = Type("!phys/kin", libkin.kin,
           libkin.kin._asdict,
           lambda x: libkin.kin(**x))

rot = Type("!phys/rot", libquat.rot,
           libquat.rot._asdict,
           lambda x: libquat.rot(**x))


@Image(".phys@force",
       usr=Node(evs=(), args=("m",),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("F_bar",),
               outs=(True,), pros=("t", "r_bar", "v_bar")))
def force(usr, fun, **kw):
    """Force accumulator"""
    m, = usr.args
        
    evs = yield
    while True:
        t, y = fun.reqs
        e, = fun.ins()
        (r, v) = y
        F = numpy.zeros_like(v)

        for sub in kw.values():
            sub.pros = t, r, v
            yield (sub.outs((e in evs,)),)
            F += next(sub.reqs)
        else:
            a = F / m
            y_dot = libkin.kin(v, a)
            
            fun.pros = y_dot,
            yield (fun.outs((e in evs,)),)


@Image(".phys@torque",
       usr=Node(evs=(), args=("eye",),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("M_bar",),
               outs=(True,), pros=("t", "q", "om_bar")))
def torque(usr, fun, **kw):
    """Torque accumulator"""
    eye, = usr.args
    inv_eye = scipy.linalg.inv(eye)
        
    evs = yield
    while True:
        t, y = fun.reqs
        e, = fun.ins()
        (q, om) = y
        M = - numpy.cross(om, numpy.dot(eye, om))

        for sub in kw.values():
            sub.pros = t, q, om
            yield (sub.outs((e in evs,)),)
            M += next(sub.reqs)
        else:
            q_dot = q * (om / 2)
            om_dot = numpy.dot(inv_eye, M)
            y_dot = libquat.rot(q_dot, om_dot)
            
            fun.pros = y_dot,
            yield (fun.outs((e in evs,)),)


@Image(".phys@lerp",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(False,), args=("t", "y"),
                ins=(False,), reqs=("t", "y"),
                outs=(True,), pros=("t", "y")),
       fun=Node(evs=(True,), args=(),
                ins=(), reqs=("t", "y"),
                outs=(), pros=("t", "y")),
       clk=Node(evs=(), args=("h",),
                ins=(), reqs=(),
                outs=(True,), pros=("t",)))
def lerp(env, sys, fun, clk):
    """Cubic Hermite spline"""
    sys_t, sys_y1 = sys.args
    clk_h, = clk.args
    
    evs = yield
    while True:
        env_t, = env.reqs
        sys_data = sys.reqs
        sys_e, = sys.ins()
        if env_t >= sys_t or sys_e in evs:
            if sys_e in evs:
                sys_t, sys_y1 = sys_data
            fun.pros = env_t, sys_y1
            clk.pros = env_t + clk_h,
            yield (clk.outs((True,)),)
            sys_y0 = sys_y1
            sys_t, sys_y1 = fun.reqs
        
        p0, m0 = sys_y0
        p1, m1 = sys_y1
        x = 1 - (sys_t - env_t) / clk_h
        
        h00 = 2 * x ** 3 - 3 * x ** 2 + 1
        h10 = x ** 3 - 2 * x ** 2 + x
        h01 = - 2 * x ** 3 + 3 * x ** 2
        h11 = x ** 3 - x ** 2
        p = (h00 * p0 +
             h10 * clk_h * m0 +
             h01 * p1 +
             h11 * clk_h * m1)
        
        g00 = 6 * x ** 2 - 6 * x
        g10 = 3 * x ** 2 - 4 * x + 1
        g01 = - 6 * x ** 2 + 6 * x
        g11 = 3 * x ** 2 - 2 * x
        m = (g00 * p0 / clk_h +
             g10 * m0 +
             g01 * p1 / clk_h +
             g11 * m1)
        
        sys_y = libkin.kin(p, m)
        sys.pros = env_t, sys_y
        yield (sys.outs((True,)),)


@Image(".phys@slerp",
       env=Node(evs=(True,), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=(False,), args=("t", "y"),
                ins=(False,), reqs=("t", "y"),
                outs=(True,), pros=("t", "y")),
       fun=Node(evs=(True,), args=(),
                ins=(), reqs=("t", "y"),
                outs=(), pros=("t", "y")),
       clk=Node(evs=(), args=("h",),
                ins=(), reqs=(),
                outs=(True,), pros=("t",)))
def slerp(env, sys, fun, clk):
    """Spherical cubic interpolation"""
    sys_t, sys_y1 = sys.args
    clk_h, = clk.args
    
    evs = yield
    while True:
        env_t, = env.reqs
        sys_data = sys.reqs
        sys_e, = sys.ins()
        if env_t >= sys_t or sys_e in evs:
            if sys_e in evs:
                sys_t, sys_y1 = sys_data
            fun.pros = env_t, sys_y1
            clk.pros = env_t + clk_h,
            yield (clk.outs((True,)),)
            sys_y0 = sys_y1
            sys_t, sys_y1 = fun.reqs
            
        q0, om0 = sys_y0
        q1, om1 = sys_y1
        x = 1 - (sys_t - env_t) / clk_h
        
        q0_dot = q0 * (om0 / 2)
        q1_dot = q1 * (om1 / 2)
        
        h00 = 2 * x ** 3 - 3 * x ** 2 + 1
        h10 = x ** 3 - 2 * x ** 2 + x
        h01 = - 2 * x ** 3 + 3 * x ** 2
        h11 = x ** 3 - x ** 2
        q = (h00 * q0 +
             h10 * clk_h * q0_dot +
             h01 * q1 +
             h11 * clk_h * q1_dot)
        
        g00 = 6 * x ** 2 - 6 * x
        g10 = 3 * x ** 2 - 4 * x + 1
        g01 = - 6 * x ** 2 + 6 * x
        g11 = 3 * x ** 2 - 2 * x
        q_dot = (g00 * q0 / clk_h +
                 g10 * q0_dot +
                 g01 * q1 / clk_h +
                 g11 * q1_dot)
        
        om = 2 * (~q) * q_dot
        
        sys_y = libquat.rot(q, om)
        sys.pros = env_t, sys_y
        yield (sys.outs((True,)),)
