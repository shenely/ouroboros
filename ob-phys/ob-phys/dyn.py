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
__all__ = ("kin",
           "force", "torque")

kin = Type(".phys#kin", "!phys/kin", libkin.kin,
           libkin.kin._asdict,
           lambda x: libkin.kin(**x))

rot = Type(".phys#rot", "!phys/rot", libquat.rot,
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
    m, = next(usr.data)
    all(next(sub.data)
        for sub in kw.values())
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        (r, v) = y
        F = numpy.zeros_like(v)

        for sub in kw.values():
            sub.data.send((t, r_bar, v_bar))
            yield (sub.ctrl.send((e in evs,)),)
            F += next(next(sub.data))
        else:
            a = F / m
            y_dot = libkin.kin(v, a)
            
            fun.data.send((y_dot,))
            yield (fun.ctrl.send((e in evs,)),)


@Image(".phys@torque",
       usr=Node(evs=(), args=("eye",),
                ins=(), reqs=(),
                outs=(), pros=()),
       fun=Node(evs=(True,), args=(),
                ins=(True,), reqs=("t", "y"),
                outs=(False,), pros=("y_dot",)),
       kw=Node(evs=(False,), args=(),
               ins=(), reqs=("M",),
               outs=(True,), pros=("t", "q", "om")))
def torque(usr, fun, **kw):
    """Torque accumulator"""
    eye, = next(usr.data)
    inv_eye = scipy.linalg.inv(eye)
    all(next(sub.data)
        for sub in kw.values())
        
    evs = yield
    while True:
        t, y = next(fun.data)
        e, = next(fun.ctrl)
        (q, om) = y
        M = - numpy.cross(om, numpy.dot(eye, om)))

        for sub in kw.values():
            sub.data.send((t, r_bar, v_bar))
            yield (sub.ctrl.send((e in evs,)),)
            M += next(next(sub.data))
        else:
            q_dot = q, * (om / 2)
            om_dot = numpy.dot(inv_eye, M)
            y_dot = libquat.rot(q_dot, om_dot)
            
            fun.data.send((y_dot,))
            yield (fun.ctrl.send((e in evs,)),)
            
