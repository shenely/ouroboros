#built-in libraries
import collections
import functools
import logging

#external libraries
#...

#internal libraries
#...

#exports
__all__ = ('CATELOG',
           'CRITICAL', 'HIGH', 'NORMAL', 'LOW', 'TRIVIAL',
           'coroutine', 'Item', 'PROCESS',
           'step', 'init')

#constants
CATELOG = {}#process catelog

#priorities
CRITICAL = 1
HIGH     = 10
NORMAL   = 100
LOW      = 1000
TRIVIAL  = 10000

EMPTY = {'data': {}, 'ctrl': {}}

Item = collections.namedtuple('Item', ('tag',
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
    items = {item.tag: item for item in items}
    def decorator(func):
        func = coroutine(func)
        @functools.wraps(func)
        def wrapper(sys, maps, keys):
            try:
                #Pull arguments and events from items
                args = {tag:
                        (lambda tag, names:
                         ((sys[name]['data']
                           [maps[tag]['data'].get(key, key)
                            if maps is not None
                            and tag in maps
                            else key]
                           for key in items[tag].args)
                          for name in names))
                        (tag, names)
                        for tag, names in keys.iteritems()}
                evs = (sys[name]['ctrl']
                       [maps[tag]['ctrl'].get(key, key)
                        if maps is not None
                        and tag in maps
                        else key]
                       for tag, names in keys.iteritems()
                       for name in names
                       for key in items[tag].evs)
                gen = func(**args)#create generator

                evs = yield evs
                while True:
                    #XXX this mess actually calls the function
                    right = {tag:
                             (lambda tag, names:
                              (((sys[name]['data']
                                 [maps[tag]['data'].get(key, key)
                                  if maps is not None
                                  and tag in maps
                                  else key]
                                 for key in items[tag].reqs),
                                (sys[name]['ctrl']
                                 [maps[tag]['ctrl'].get(key, key)
                                  if maps is not None
                                  and tag in maps
                                  else key] in evs
                                 for key in items[tag].ins))
                               for name in names))
                             (tag, names)
                             for tag, names in keys.iteritems()}
                    left = gen.send(right)
                    evs = yield (ev for tag, names
                                 in keys.iteritems()
                                 if tag in left
                                 for name, (pros, outs)
                                 in zip(names, left[tag])
                                 for ev in
                                 (pros is not None and
                                  (sys[name]['data'].update
                                   ({(maps[tag]['data'].get(key, key)
                                      if maps is not None
                                      and tag in maps
                                      else key):
                                     logging.info('data:%s:%s',
                                                  key, pro) or pro
                                     for key, pro
                                     in zip(items[tag].pros, pros)
                                     if pro is not None})) or
                                  (logging.info('ctrl:%s', key) or
                                   sys[name]['ctrl']
                                   [maps[tag]['ctrl'].get(key, key)
                                    if maps is not None
                                    and tag in maps
                                    else key]
                                   for key, out
                                   in zip(items[tag].outs, outs)
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
              evs=(), args=('e',),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('F',
              evs=(None, True), args=('n',),
              ins=(), reqs=(),
              outs=(True,), pros=('n',)))
def step(T, F):
    e, = T.next()
    n, = F.next()
    while True:
        #logging.info('%d', n)
        e.clear()
        F = ((n,), (True,)),
        yield {'F': F}
        n += 1

@PROCESS('core.init', CRITICAL,
         Item('ing',
              evs=('e',), args=(),
              ins=(), reqs=(),
              outs=(), pros=()),
         Item('egr',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=('e',), pros=()))
def init(ing, egr):
    right = yield
    while True:
        egr = right['egr']
        egr = (((), (True,)) for _ in egr)
        left = {'egr': egr}
        right = yield left
