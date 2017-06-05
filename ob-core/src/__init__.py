#built-in libraries
import collections
import functools
import logging

#external libraries
#...

#internal libraries
#...

#exports
__all__ = ['CATELOG',
           'CRITICAL', 'HIGH', 'NORMAL', 'LOW', 'TRIVIAL',
           'coroutine', 'Item', 'PROCESS']

#constants
CATELOG = {}#process catelog

#priorities
CRITICAL = 1
HIGH     = 10
NORMAL   = 100
LOW      = 1000
TRIVIAL  = 10000

Item = collections.namedtuple('Item', ('name',
                                       'evs', 'args',
                                       'ins', 'reqs',
                                       'outs', 'pros'))

def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    return wrapper

def PROCESS(name, level=NORMAL, *items):
    def decorator(func):
        func = coroutine(func)
        @functools.wraps(func)
        def wrapper(sys, *confs):
            try:
                #Pull arguments and events from items
                args = ((lambda conf, item:
                         ((sys[name]['data'][key]
                           for key in item.args)
                          for name in conf))
                         (conf, item)
                        for conf, item in zip(confs, items))
                evs = (sys[name]['ctrl'][key]
                       for conf, item in zip(confs, items)
                       for name in conf
                       for key in item.evs)
                gen = func(*args)#create generator

                evs = yield evs
                while True:
                    #XXX this mess actually calls the function
                    right = ((lambda conf, item:
                              (((sys[name]['data'][key]
                                 for key in item.reqs),
                                (sys[name]['ctrl'][key] in evs
                                 for key in item.ins))
                               for name in conf))
                             (conf, item)
                             for conf, item in zip(confs, items))
                    left = gen.send(right)
                    evs = yield (ev for n, (names, item) in
                                 enumerate(zip(confs, left))
                                 if item is not None
                                 for name, (pros, outs) in
                                 zip(names, item)
                                 for ev in
                                 (sys[name]['data'].update
                                  ({key: pro for key, pro in
                                    zip(items[n].pros, pros)
                                    if pro is not None}) or
                                  (sys[name]['ctrl'][key]
                                   for key, out in
                                   zip(items[n].outs, outs)
                                   if out)))
            except StopIteration:
                return
            finally:
                pass
        CATELOG[name] = level, wrapper
        return wrapper
    return decorator

@PROCESS('core.step', TRIVIAL,
         Item('T',
              evs=(None,), args=('e',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('F',
              evs=(None,), args=('n',),
              ins=(), reqs=(),
              outs=(None,), pros=('n',)))
def step(T, F):
    e, = T.next()
    n, = F.next()
    yield
    while True:
        logging.info('%d', n)
        e.clear()
        F = ((n,), (True,)),
        yield None, F
        n += 1
