import time
import functools
import logging

import numpy
import tornado

from ouroboros.__main__ import main

logging.basicConfig(level=logging.INFO)

O_BAR = numpy.array([0,0,0])
I_HAT = numpy.array([1,0,0])
J_HAT = numpy.array([0,1,0])
K_HAT = numpy.array([0,0,1])

args = [{'name': None,
         'mem': {(None, None): {'data': {},
                                'ctrl': []},
                 (True, None): {'data': {'t': time.time()},
                                'ctrl': []},
                 (False, None): {'data': {'t': 0.0, 'x': 1.0},
                                 'ctrl': [False, True]}},
         'exe': []},
        {'name': 'clock',
         'mem': {(None, None): None,
                 (True, None): {'data': {'delta_t': 1.0},
                                'ctrl': ['tick']},
                 (False, None): {'data': {'t_dt': None},
                                 'ctrl': ['tock', 8601]}},
          'exe': [{'tag': 'clock.every',
                   'map': {'env': {'data': {},
                                   'ctrl': {'tick': True}}},
                   'key': {'env': [(None, None)],
                           'sys': [(True, None)],
                           'usr': [(False, None)]}},
                  {'tag': 'clock.iso8601',
                   'map': None,
                   'key': {'sys': [(None, None)],
                           'usr': [(False, None)]}}]}]

tornado.ioloop.IOLoop.current().run_sync(functools.partial(main, *args))
