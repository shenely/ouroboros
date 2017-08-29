import time
import logging

import numpy

from ouroboros.__main__ import main

logging.basicConfig(level=logging.INFO)

O_BAR = numpy.array([0,0,0])
I_HAT = numpy.array([1,0,0])
J_HAT = numpy.array([0,1,0])
K_HAT = numpy.array([0,0,1])

args = [{'name': None,
         'items': {(True, None): {'data': {'q': [],
                                           'e': set()},
                                  'ctrl': []},
                   (False, None): {'data': {'m': 0},
                                   'ctrl': [None, True]}},
         'procs': [{'tag': 'core.step',
                    'maps': {'F': {'data': {'n': 'm'},
                                   'ctrl': {}}},
                    'keys': {'T': [(True, None)],
                             'F': [(False, None)]}}]},
        {'name': 'clock',
         'items': {(None, None): None,
                   (True, None): {'data': {'q': [],
                                           't': time.time(),
                                           'delta_t': 1.0,
                                           't_dt': None},
                                  'ctrl': ['tick', 8601]},
                   (False, None): {'data': {'q': [],
                                            't': 0.0,
                                            'delta_t': 1.0,
                                            't_dt': None},
                                   'ctrl': ['tick', 8601]},
                   ('timer', '+1*'): {'data': {'t': 0.0,
                                               'delta_t': 1.0,
                                               'n': -1},
                                      'ctrl': ['tock']}},
          'procs': [{'tag': 'clock.scaled',
                     'maps': None,
                     'keys': {'env': [(None, None)],
                              'sys': [(True, None)],
                              'clk': [(False, None)]}},
                    {'tag': 'clock.timer',
                     'maps': None,
                     'keys': {'clk': [(False, None)],
                              'usr': [('timer', '+1*')]}},
                    {'tag': 'clock.iso8601',
                     'maps': None,
                     'keys': {'clk': [(True, None),
                                      (False, None)]}}]},
        {'name': 'earth',
         'items': {(False, True): {'data': {'mu': 398600.4},
                                   'ctrl': []}},
         'procs': []},
        {'name': 'iss',
         'items': {(None, None): None,
                   ('clock', None): None,
                   ('earth', True): None,
                   (True, 'tle'): {'data': {'inc': 51.6416,
                                            'raan': 247.4627,
                                            'ecc': 0.0006703,
                                            'aop': 130.5360,
                                            'ma': 325.0288,
                                            'mm': 15.72125},
                                   'ctrl': [2]},
                   (False, True): {'data': {'r_bar': O_BAR,
                                            'v_bar': O_BAR},
                                   'ctrl': ['rec']}},
         'procs': [{'tag': 'core.init',
                    'maps': {'ing': {'data': {},
                                     'ctrl': {'e': None}},
                             'egr': {'data': {},
                                     'ctrl': {'e': 2}}},
                    'keys': {'ing': [(None, None)],
                             'egr': [(True, 'tle')]}},
                   {'tag': 'orb.tle',
                    'maps': None,
                    'keys': {'bod': [('earth', True)],
                             'tle': [(True, 'tle')],
                             'rec': [(False, True)]}}]}]

main(*args)
