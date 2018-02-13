#built-in libraries
import time
import datetime
import heapq
import logging

#external libraries
import pytz

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__= ('at', 'after', 'every',
          'relate', 'iso8601')

#constants
#...

@PROCESS('clock.at', NORMAL,
         Item('sys',
              evs=('tick',), args=(),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('tock',), pros=()))
def at(sys, usr):
    """at"""
    sys_t, = sys.next()
    
    right = yield
    while True:
        sys, usr = (right['sys'],
                    right['usr'])
        (sys_t,), _ = sys.next()
        usr = (((), (sys_t,))
               for _ in usr)
        left = {'usr': usr}
        right = yield left

@PROCESS('clock.after', NORMAL,
         Item('env',
              evs=(), args=(),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('sys',
              evs=('tick',), args=(),
              ins=(), reqs=('delta_t',),
              outs=(), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('tock',), pros=()))
def after(env, sys, usr):
    """after"""
    
    right = yield
    while True:
        env, sys, usr = (right['env'],
                         right['sys'],
                         right['usr'])
        (env_t,), _ = env.next()
        (delta_t,), _ = sys.next()
        usr = (((), (env_t + delta_t,))
               for _ in usr)
        left = {'usr': usr}
        right = yield left

@PROCESS('clock.every', NORMAL,
         Item('env',
              evs=('tick',), args=('t',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sys',
              evs=('tick',), args=('delta_t',),
              ins=(), reqs=(),
              outs=('tick',), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('tock',), pros=()))
def every(env, sys, usr):
    """every"""
    env_t, = env.next()
    delta_t, = sys.next()
    
    right = yield
    while True:
        usr = right['usr']
        env_t += delta_t
        sys = (((), (env_t,)),)
        usr = (((), (True,))
               for _ in usr)
        left = {'sys': sys, 'usr': usr}
        right = yield left

@PROCESS('clock.relate', NORMAL,
         Item('sys',
              evs=('tick',), args=(),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=('<', '=', '>'), reqs=('t',),
              outs=('<', '=', '>'), pros=()))
def relate(sys, usr):
    """relate"""
    right = yield
    while True:
        sys, usr = (right['sys'],
                    right['usr'])
        
        (sys_t,), (sys_e,) = sys.next()
        usr = (((), ((sys_t < usr_t) if usr_lt is not True else None,
                     (sys_t == usr_t) if usr_eq is not True else None,
                     (sys_t > usr_t) if usr_gt is not True else None))
               for ((usr_t,), (usr_lt, usr_eq, usr_gt)) in usr)

        left = {'usr': usr}
        right = yield left

@PROCESS('clock.iso8601', NORMAL,
         Item('sys',
              evs=(), args=(),
              ins=(), reqs=('t',),
              outs=(), pros=()),
         Item('usr',
              evs=('tock',), args=(),
              ins=('tock', 8601,), reqs=(),
              outs=(8601,), pros=('t_dt',)))
def iso8601(sys, usr):
    right = yield
    while True:
        sys, usr = (right['sys'],
                    right['usr'])
        (sys_t,), _ = sys.next()
        _, (clk_e, usr_e,) = usr.next()

        usr = (((datetime.datetime
                 .fromtimestamp
                 (sys_t, tz=pytz.utc),), (True,))
               if clk_e is True and usr_e is not True
               else ((None,), (None,)),)

        left = {'usr': usr}
        right = yield left
