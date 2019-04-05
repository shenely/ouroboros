import math
import time
import pickle

args = [
    {
        'name': None,
        'items': {
            (None, None): {
                'data': {},
                'ctrl': []
            },
            (True, None): {
                'data': {'t': None},
                'ctrl': []
            },
            (False, None): {
                'data': {'t': 0.0, 'x': 1.0},
                'ctrl': [False, True]
            }
        },
        'procs': []
    },
    {
        'name': 'clock',
        'items': {
            (None, None): None,
            (False, 1): {
                'data': {'delta_t': 1.0},
                'ctrl': [True]
            },
            (False, 'time'): {
                'data': {'t_dt': None},
                'ctrl': [True, 8601]
            }
        },
        'procs': [
            {
                'p': 100,
                'tag': 'clock.every',
                'keys': {
                    'env': (None, None),
                    'sys': (False, 1),
                    'usr': (False, 'time')
                },
                'maps': {
                    'env': {
                        'data': {},
                        'ctrl': {'tick': True}
                    },
                    'sys': {
                        'data': {},
                        'ctrl': {'tick': True}
                    },
                    'usr': {
                        'data': {},
                        'ctrl': {'tock': True}
                    }
                }
            },
            {
                'p': 100,
                'tag': 'clock.iso8601',
                'keys': {
                    'sys': (None, None),
                    'usr': (False, 'time')
                },
                'maps': {
                    'usr': {
                        'data': {},
                        'ctrl': {'tock': True}
                    }
                }
            }
        ]
    }
]
##        {'name': 'test',
##         'mem': {(None, None): None,
##                 ('clock', 'time'): None,
##                 ('clock', 2): None,
##                 ('clock', 3): None,
##                 ('clock', 5): None,
##                 (False, 'inc'): {'data': {'byte': 0, 'bit': 0,
##                                           'size': 6,
##                                           'raw': None, 'eng': 0},
##                                  'ctrl': ['inc', 'raw', 'eng']},
##                 (False, 'rand'): {'data': {'byte': 0, 'bit': 6,
##                                            'size': 10,
##                                            'lower': 0.0, 'upper': 1.0,
##                                            'raw': None, 'eng': None},
##                                   'ctrl': ['rand', 'raw', 'eng']},
##                 (False, 'test'): {'data': {'size': 16,
##                                            'raw': None},
##                                   'ctrl': ['raw', 'eng']},},
##         'exe': [{'tag': 'clock.every',
##                  'map': {'env': {'data': {},
##                                  'ctrl': {'tick': True}},
##                          'usr': {'data': {},
##                                  'ctrl': {'tock': 'inc'}}},
##                  'key': {'env': [(None, None)],
##                          'sys': [('clock', 2)],
##                          'usr': [(False, 'inc')]}},
##                 {'tag': 'clock.every',
##                  'map': {'env': {'data': {},
##                                  'ctrl': {'tick': True}},
##                          'usr': {'data': {},
##                                  'ctrl': {'tock': 'rand'}}},
##                  'key': {'env': [(None, None)],
##                          'sys': [('clock', 3)],
##                          'usr': [(False, 'rand')]}},
##                 {'tag': 'clock.every',
##                  'map': {'env': {'data': {},
##                                  'ctrl': {'tick': True}},
##                          'usr': {'data': {},
##                                  'ctrl': {'tock': 'eng'}}},
##                  'key': {'env': [(None, None)],
##                          'sys': [('clock', 5)],
##                          'usr': [(False, 'test')]}},
##                 {'tag': 'fun.inc',
##                  'map': {'usr': {'data': {'x': 'eng'},
##                                  'ctrl': {}}},
##                  'key': {'usr': [(False, 'inc')]}},
##                 {'tag': 'fun.rand',
##                  'map': {'usr': {'data': {'x': 'eng'},
##                                  'ctrl': {}}},
##                  'key': {'usr': [(False, 'rand')]}},
##                 {'tag': 'data.raw.format',
##                  'map': None,
##                  'key': {'usr': [(False, 'inc')]}},
##                 {'tag': 'data.lin.format',
##                  'map': None,
##                  'key': {'usr': [(False, 'rand')]}},
##                 {'tag': 'data.struct.format',
##                  'map': None,
##                  'key': {'mne': [(False, 'inc'),
##                                  (False, 'rand')],
##                          'usr': [(False, 'test')]}},]},]
##        {'name': 'iss',
##         'mem': {(None, None): None,
##                 ('clock', 'time'): None,
##                 (False, 2): {'data': {2: ['ISS (ZARYA)',
##                                           '1 25544U 98067A   18184.80969102  .00001614  00000-0  31745-4 0  9993',
##                                           '2 25544  51.6414 295.8524 0003435 262.6267 204.2868 15.54005638121106']},
##                              'ctrl': []},
##                 (True, 4): {'data': {4: None},
##                             'ctrl': [4]},
##                 (False, 'rec'): {'data': {'r_bar': None,
##                                           'v_bar': None},
##                                  'ctrl': ['rec']}},
##         'exe': [{'tag': 'orb.tle2sgp',
##                  'map': None,
##                  'key': {'env': [(None, None)],
##                          'tle': [(False, 2)],
##                          'sgp': [(True, 4)]}},
##                 {'tag': 'orb.sgp4tle',
##                  'map': None,
##                  'key': {'clk': [('clock', 'time')],
##                          'sgp': [(True, 4)],
##                          'orb': [(False, 'rec')]}}]},]
##        {'name': 'test',
##         'mem': {(None, None): None,
##                 (True, 'fun'): {'data': {'k': 1.0,
##                                          't': None,
##                                          'y': None,
##                                          'f': None},
##                                 'ctrl': ['i', 'o']},
##                 (False, 'sys'): {'data': {'y': 1.0},
##                                  'ctrl': ['ode']},
##                 (False, 'usr'): {'data': {'h': 0.25},
##                                  'ctrl': [True, False]}},
##         'exe': [{'tag': 'ode.euler',
##                  'map': None,
##                  'key': {'env': [(None, None)],
##                          'sys': [(False, 'sys')],
##                          'fun': [(True, 'fun')],
##                          'usr': [(False, 'usr')]}},
##                 {'tag': 'ode.exp',
##                  'map': None,
##                  'key': {'fun': [(True, 'fun')]}}]}]

if __name__ == '__main__':
    with open('../test.pkl', 'wb') as pkl:
        pickle.dump(args, pkl)
