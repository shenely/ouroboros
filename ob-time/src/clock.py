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
__all__= ('scaled', 'timer', 'relate', 'iso8601')

#constants
#...

@PROCESS('clock.scaled', NORMAL,
         Item('env',
              evs=(True,), args=(),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('sys',
              evs=(), args=('t', 'q'),
              ins=(), reqs=('delta_t',),
              outs=('tick',), pros=('t',)),
         Item('clk',
              evs=(), args=('t', 'q'),
              ins=(), reqs=('delta_t',),
              outs=('tick',), pros=('t',)))
def scaled(env, sys, clk):
    """Scaled (real-time) clock"""
    sys_t0, sys_q = sys.next()
    clk_t0, clk_q = clk.next()
    corr = 0.0

    right = yield
    while True:
        sys, clk = right['sys'], right['clk']
        
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
         
        delta = sys_t - time.time() + corr
        if sys_t != sys_t0:
            logging.info('%f%%', 100 * (1 - delta / sys_dt))
        if delta > 0:time.sleep(delta)
        error = sys_t - time.time()
        if error > 0:time.sleep(error)
        corr += error
        
        sys_t = time.time()
        clk_t = clk_t0 + (sys_t - sys_t0) * scale
        
        logging.info('%f, %f', sys_t, clk_t)
        sys = (((sys_t,), (True,)),)
        clk = (((clk_t,), (True,)),)
        sys_t0, clk_t0 = sys_t, clk_t

        left = {'sys': sys, 'clk': clk}
        right = yield left

@PROCESS('clock.timer', NORMAL,
         Item('clk',
              evs=('tick',), args=('q',),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('usr',
              evs=(), args=('t',),
              ins=('tock',), reqs=('t', 'delta_t', 'n'),
              outs=('tock',), pros=('t', 'n')))
def timer(clk, usr):
    """Timer"""
    q, = clk.next()
    any(heapq.heappush(q, usr_t)
        for usr_t, in usr)
    
    right = yield
    while True:
        clk, usr = right['clk'], right['usr']
        
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
                  ((usr_t, usr_n), (True,)))
                 if usr_t is not None else
                 ((None, None), (False,)))
                for (usr_t, usr_n) in usr)
               if usr is not None else None)

        left = {'usr': usr}
        right = yield left

@PROCESS('clock.relate', NORMAL,
         Item('clk',
              evs=('tick',), args=(),
              ins=('tick',), reqs=('t',),
              outs=(), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=('<', '=', '>'), reqs=('t',),
              outs=('<', '=', '>'), pros=()))
def relate(clk, usr):
    """relate"""
    right = yield
    while True:
        clk, usr = right['clk'], right['usr']
        
        (clk_t,), (clk_e,) = clk.next()
        usr = ((((), (not usr_lt and (clk_t < usr_t),
                      not usr_eq and (clk_t == usr_t),
                      not usr_gt and clk_t > usr_t))
                for ((usr_t,), (usr_lt, usr_eq, usr_gt)) in usr)
               if clk_e else None)

        left = {'usr': usr}
        right = yield left

@PROCESS('clock.iso8601', NORMAL,
         Item('clk',
              evs=('tick',), args=(),
              ins=('tick', 8601), reqs=('t',),
              outs=(8601,), pros=('t_dt',)))
def iso8601(clk):
    right = yield
    while True:
        clk = right['clk']
        
        clk = ((datetime.datetime
                .fromtimestamp
                (clk_t, tz=pytz.utc)
                if clk_e and not iso_e
                else None)
               for (clk_t,), (clk_e, iso_e) in clk)
        clk = ((((iso_t,), (True,))
                if iso_t is not None else
                ((None,), (False,)))
               for iso_t in clk)

        left = {'clk': clk}
        right = yield left
