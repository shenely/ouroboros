# built-in libraries
import datetime

# external libraries
import pytz

# internal libraries
from ouroboros import Type, Image, Node
from ouroboros.conf import MILLI, UNIX_EPOCH

# exports
__all__= ("dt", "td",
          "at", "after", "every",
          "relate", "iso8601")

# constants
# ...

# datetime.datetime <-> JSON
dt = Type(".clock#dt", "!clock/dt", datetime.datetime,
          lambda x: int((x - UNIX_EPOCH).total_seconds() / MILLI),
          lambda x: UNIX_EPOCH + datetime.timedelta(seconds=x * MILLI))

# datetime.timedelta <-> JSON
td = Type(".clock#td", "!clock/td", datetime.timedelta,
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
        sys_t, = sys.reqs
        yield (usr.outs((sys_t,)),)


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
        env_t, = env.reqs
        delta_t, = sys.reqs
        yield (usr.outs((env_t + delta_t,)),)


@Image(".clock@every",
       env=Node(evs=("tick",), args=("t",),
                ins=(), reqs=(),
                outs=(), pros=()),
       sys=Node(evs=("tick",), args=("delta_t",),
                ins=(), reqs=(),
                outs=("tick",), pros=()),
       kw=Node(evs=(), args=(),
               ins=(), reqs=(),
               outs=("tock",), pros=()))
def every(env, sys, **kw):
    """every"""
    env_t, = env.args
    delta_t, = sys.args
    
    yield
    while True:
        env_t += delta_t
        yield ((sys.outs((env_t,)),) +
               tuple(usr.outs((True,))
                     for usr in kw.values()))


@Image(".clock@relate",
       sys=Node(evs=("tock",), args=(),
                ins=(), reqs=("t",),
                outs=(), pros=()),
       usr=Node(evs=(), args=(),
                ins=(), reqs=("t",),
                outs=("lt", "eq", "gt"), pros=()))
def relate(sys, usr):
    """relate"""
    evs = yield
    while True:
        sys_t, = env.reqs
        usr_t, = usr.reqs
        yield (usr.outs((sys_t < usr_t,
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
        sys_t, = sys.reqs
        clk_e, usr_e = usr.ins()
        flag = usr_e not in evs
        if flag:
            usr.pros = (datetime.datetime.fromtimestamp
                        (sys_t, tz=pytz.utc),)
        yield (usr.outs((flag or None,)),)
