#built-in libraries
import datetime

#external libraries
import pytz

#internal libraries
from ouroboros import Type, Image, Node

#exports
__all__= ("dt", "td",
          "at", "after", "every",
          "relate", "iso8601")

#constants
MILLI = 1e-3  # seconds

UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

# datetime.datetime <-> JSON
dt = Type(".clock#dt", datetime.datetime,
          lambda x: int((x - UNIX_EPOCH).total_seconds() / MILLI),
          lambda x: UNIX_EPOCH + datetime.timedelta(seconds=x * MILLI))

# datetime.timedelta <-> JSON
td = Type(".clock#td", datetime.timedelta,
          lambda x: int(x.total_seconds() / MILLI),
          lambda x: datetime.timedelta(seconds=x * MILLI))


@Image(".clock@at",
       sys=Node(evs=("tick",), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       usr=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("tock",), pros=()))
def at(sys, usr):
    """at"""    
    yield
    while True:
        sys_t, = next(sys.data)
        yield (usr.ctrl.send((sys_t,)),)


@Image(".clock@after",
       env=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       sys=Node(evs=("tick",), args=(),
                ins=(), reqs=("delta_t",),
                outs=(), pros=()),
       usr=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("tock",), pros=()))
def after(env, sys, usr):
    """after"""
    yield
    while True:
        env_t, = next(env.data)
        delta_t, = next(sys.data)
        yield (usr.ctrl.send((env_t + delta_t,)),)


@Image(".clock@every",
       env=Node(evs=("tick",), args=("t",),
                ins=(), reqs=(),
                outs=(), pros=()),
       sys=Node(evs=("tick",), args=("delta_t",),
                ins=(), reqs=(),
                outs=("tick",), pros=()),
       usr=Node(evs=(), args=(),
                ins=(), reqs=(),
                outs=("tock",), pros=()))
def every(env, sys, usr):
    """every"""
    env_t, = next(env.data)
    delta_t, = next(sys.data)
    
    yield
    while True:
        env_t += delta_t
        yield (sys.ctrl.send((env_t,)),
               usr.ctrl.send((True,)))


@Image(".clock@relate",
       sys=Node(evs=("tock",), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       usr=Node(evs=(), args=(),
                ins=("<", "=", ">"), reqs=("t",),
                outs=("<", "=", ">"), pros=()))
def relate(sys, usr):
    """relate"""
    evs = yield
    while True:
        sys_t, = next(env.data)
        usr_t, = next(usr.data)
        yield (usr.ctrl.send((sys_t < usr_t,
                              sys_t == usr_t,
                              sys_t > usr_t)),)


@Image(".clock@iso8601",
       sys=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       usr=Node(evs=("tock",), args=(),
                ins=("tock", 8601,), reqs=(),
                outs=(8601,), pros=("t_dt",)))
def iso8601(sys, usr):
    evs = yield
    while True:
        sys_t, = next(sys.data)
        clk_e, usr_e = next(usr.ctrl)
        flag = usr_e not in evs
        usr.data.send((datetime.datetime.fromtimestamp
                       (sys_t, tz=pytz.utc)
                       if flag else None,))
        yield (usr.ctrl.send((flag or None,)),)
