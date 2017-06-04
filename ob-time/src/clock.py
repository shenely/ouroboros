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
__all__= ['scaled', 'timer', 'relate', 'iso8601']

#constants
#...

@PROCESS('clock.scaled', NORMAL,
         Item('environment',
              evs=(None,), args=(),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('system',
              evs=(), args=('t', 'q'),
              ins=(), reqs=('dt',),
              outs=('tick',), pros=('t',)),
         Item('clock',
              evs=(), args=('t', 'q'),
              ins=(), reqs=('dt',),
              outs=('tick',), pros=('t',)))
def scaled(env, sys, clk):
    """Scaled (real-time) clock"""
    sys_t0, sys_q = sys.next()
    clk_t0, clk_q = clk.next()
    
    _, sys, clk = yield
    while True:
        (sys_dt,), _ = sys.next()
        (clk_dt,), _ = clk.next()
        
        sys_t = (heapq.heappop(sys_q)
                 if sys_q else float('inf'))
        clk_t = (heapq.heappop(clk_q)
                 if clk_q else float('inf'))
        
        scale = clk_dt / sys_dt
        sys_t, clk_t = ((heapq.heappush(sys_q, sys_t) or
                         (sys_t0 + (clk_t - clk_t0) / scale, clk_t))
                        if ((clk_t - clk_t0) / clk_dt <=
                            (sys_t - sys_t0) / sys_dt) else
                        (heapq.heappush(clk_q, clk_t) or
                         (sys_t, clk_t + (sys_t - sys_t0) * scale)))
         
        # Sleep in a loop to fix inaccuracies of windows (see
        # http://stackoverflow.com/a/15967564 for details) and to ignore
        # interrupts.
        while True:
            delta = sys_t - time.time()
            if delta <= 0:break
            time.sleep(delta)
         
        sys_t = time.time()
        clk_t = clk_t0 +  (sys_t - sys_t0) * scale
        logging.info('%f, %f', sys_t, clk_t)
        sys = (((sys_t,), (True,)),)
        clk = (((clk_t,), (True,)),)
        _, sys, clk = yield None, sys, clk
        sys_t0, clk_t0 = sys_t, clk_t

@PROCESS('clock.timer', NORMAL,
         Item('clock',
              evs=('tick',), args=('q',),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('user',
              evs=(), args=('t',),
              ins=('tock',), reqs=('t', 'dt', 'n'),
              outs=('tock',), pros=('t', 'n')))
def timer(clk, usr):
    """Timer"""
    q, = clk.next()
    any(heapq.heappush(q, usr_t)
        for usr_t, in usr)
    clk, usr = yield
    while True:
        (clk_t,), (clk_e,) = clk.next()
        usr = ((((usr_t + usr_dt,
                  (usr_n - 1) if usr_n > 0 else usr_n)
                 if not usr_e
                 and usr_n != 0
                 and clk_t >= usr_t else
                 (None, None))
                for ((usr_t, usr_dt, usr_n), (usr_e,)) in usr)
               if clk_e else None)
        usr = ((((heapq.heappush(q, usr_t) or
                  logging.info('%f, %d', usr_t, usr_n) or
                  ((usr_t, usr_n), (True,)))
                 if usr_t is not None else
                 ((None, None), (False,)))
                for (usr_t, usr_n) in usr)
               if usr is not None else None)
        clk, usr = yield None, usr

@PROCESS('clock.relate', NORMAL,
         Item('clock',
              evs=('tick',), args=(),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('user',
              evs=(), args=(),
              ins=('<', '>'), reqs=(),
              outs=('<', '>'), pros=()))
def relate(clk, usr):
    """relate"""
    clk, usr = yield
    while True:
        (clk_t,), (clk_e,) = clk.next()
        usr = ((((), (not usr_lt and (clk_t < usr_t),
                      not usr_gt and clk_t > usr_t))
                for ((usr_t,), (usr_lt, usr_gt)) in usr)
               if clk_e else None)
        clk, usr = yield None, usr

@PROCESS('clock.iso8601', NORMAL,
         Item('clock',
              evs=('tick',), args=(),
              ins=('tick', 8601,), reqs=('t',),
              outs=(8601,), pros=('t_dt',)))
def iso8601(clk):
    clk, = yield
    while True:
        clk = ((datetime.datetime
                .fromtimestamp
                (t, tz=pytz.utc)
                if T and not e else None)
               for (t,), (T, e) in clk)
        clk = (logging.info('%s', t_dt)
               or t_dt for t_dt in clk)
        clk = ((((t_dt,), (True,))
                if t_dt is not None else
                ((None,), (False,)))
               for t_dt in clk)
        clk, = yield clk,
