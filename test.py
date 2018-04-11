import pickle

args = [{'name': None,
         'mem': {(None, None): {'data': {},
                                'ctrl': []},
                 (True, None): {'data': {'t': None},
                                'ctrl': []},
                 (False, None): {'data': {'t': 0.0, 'x': 1.0},
                                 'ctrl': [False, True]}},
         'exe': []},
        {'name': 'clock',
         'mem': {(None, None): None,
                 (True, 'time'): {'data': {'delta_t': 1.0},
                                  'ctrl': ['tick']},
                 (False, 'time'): {'data': {'t_dt': None},
                                   'ctrl': ['tock', 8601]}},
          'exe': [{'tag': 'clock.every',
                   'map': {'env': {'data': {},
                                   'ctrl': {'tick': True}}},
                   'key': {'env': [(None, None)],
                           'sys': [(True, 'time')],
                           'usr': [(False, 'time')]}},
                  {'tag': 'clock.iso8601',
                   'map': None,
                   'key': {'sys': [(None, None)],
                           'usr': [(False, 'time')]}}]}]

if __name__ == '__main__':
    with open('test.pkl', 'wb') as pkl:
        pickle.dump(args, pkl)
