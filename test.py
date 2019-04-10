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
                'data': {'t': None, 'x': None},
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
                'tag': '.clock@every',
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
                'tag': '.clock@iso8601',
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
    },
    {
        'name': 'iss',
        'items': {
            (None, None): None,
            ('clock', 'time'): None,
            (False, 2): {
                'data': {
                    2: [
                        'ISS (ZARYA)',
                        '1 25544U 98067A   19095.80969102  .00001614  00000-0  31745-4 0  9993',
                        '2 25544  51.6414 295.8524 0003435 262.6267 204.2868 15.54005638121106']},
                'ctrl': []
            },
            (True, 4): {
                'data': {4: None},
                'ctrl': [4]
            },
            (False, 'rec'): {
                'data': {'r_bar': None,
                         'v_bar': None},
                'ctrl': ['rec']
            }
        },
        'procs': [
            {
                'p': 100,
                'tag': '.orb@tle2sgp',
                'keys': {
                    'env': (None, None),
                    'tle': (False, 2),
                    'sgp': (True, 4)
                },
                'maps': {}
            },
            {
                'p': 100,
                'tag': '.orb@sgp4tle',
                'keys': {
                    'clk': ('clock', 'time'),
                    'sgp': (True, 4),
                    'orb': (False, 'rec')
                },
                'maps': {
                    'orb': {
                        'data': {},
                        'ctrl': {True: 'rec'}
                    }
                }
            }
        ]
    }
]

if __name__ == '__main__':
    with open('../test.pkl', 'wb') as pkl:
        pickle.dump(args, pkl)
