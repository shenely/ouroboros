__author__ = 'shenely'

import datetime
import csv
import types

import numpy
from scipy.optimize import linprog

time_frame = 28
flight_ops = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
]
flight_ops = {flight_ops[i]: set((i,)) \
              for i in range(len(flight_ops))}

"""
0: Off-console
1: Day shift, Shift lead
2: Day shift, SATCON
3: Night shift, Shift lead
4: Night shift, SATCON
"""

OFF_CONSOLE = set((0,))

DAY_SHIFT = set((1,2))
NIGHT_SHIFT = set((3,4))

SHIFT_LEAD = set((1,3))
SATCON = set((2,4))

ON_CONSOLE = DAY_SHIFT | NIGHT_SHIFT

ALL_SHIFTS = OFF_CONSOLE | ON_CONSOLE

ALL_OPS_ENGS = flight_ops["A"] | \
               flight_ops["B"] | \
               flight_ops["C"] | \
               flight_ops["D"]

ALL_SHIFT_LEADS = flight_ops["E"] | \
                  flight_ops["F"] | \
                  flight_ops["G"] | \
                  flight_ops["H"]

ALL_SATCONS = flight_ops["I"] | \
              flight_ops["J"] | \
              flight_ops["K"] | \
              flight_ops["L"]

EVERYBODY = ALL_OPS_ENGS | ALL_SHIFT_LEADS | ALL_SATCONS

date_range = range(time_frame)

MONDAY = set([i for i in date_range
              if i % 7 == 0])
TUESDAY = set([i for i in date_range
               if i % 7 == 1])
WEDNESDAY = set([i for i in date_range
                 if i % 7 == 2])
THURSDAY = set([i for i in date_range
                if i % 7 == 3])
FRIDAY = set([i for i in date_range
              if i % 7 == 4])
SATURDAY = set([i for i in date_range
                if i % 7 == 5])
SUNDAY = set([i for i in date_range
              if i % 7 == 6])

WEEKDAY = MONDAY | TUESDAY | WEDNESDAY | THURSDAY | FRIDAY
WEEKEND = SATURDAY | SUNDAY

EVERYDAY = WEEKDAY | WEEKEND

WEEK = [set(range(7*i, min(7*(i+1), len(date_range))))
        for i in range(time_frame/7)]

def set_of_who(who):
    return flight_ops[who] \
           if isinstance(who, types.StringTypes) and \
              who in flight_ops else \
           set((who,)) \
           if isinstance(who, types.IntType) else \
           reduce(lambda a,b:a|b,
                  [flight_ops[me]
                   for me in who
                   if me in flight_ops]) \
           if isinstance(who, types.ListType) else \
           who \
           if isinstance(who, set) else \
           set()

def set_of_what(what):
    return what

def set_of_when(when):
    return [date_range.index(when)] \
           if isinstance(when, types.IntType) and \
              when in date_range else \
           set([date_range.index(now)
                for now in when
                if now in date_range]) \
           if isinstance(when, types.ListType) else \
           when \
           if isinstance(when, set) else \
           set()

def match_indices(self,other):
    other = other * len(self)
    self = sorted(self * (len(other) / len(self)))

    return self,other

def singular_shift(what):
    what = set_of_what(what)

    what = list(what)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]):
                a = numpy.zeros_like(c)
                a[i,what,j] = 1

                A_ub = numpy.append(A_ub, [a], 0)
                b_ub = numpy.append(b_ub, [1], 0)
        else:
            return A_ub, b_ub, A_eq, b_eq

    return function

def transition_shift(start, end, off=1):
    start = set_of_what(start)
    end = set_of_what(end)

    start = list(start)
    end = list(end)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]-off):
                a = numpy.zeros_like(c)
                a[i,start,j] = 1
                a[i,end,j+off] = 1

                A_ub = numpy.append(A_ub, [a], 0)
                b_ub = numpy.append(b_ub, [1], 0)
        else:
            return A_ub, b_ub, A_eq, b_eq

    return function

def consecutive_shifts(what, value):
    what = set_of_what(what)

    what = list(what)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]-value):
                a = numpy.zeros_like(c)
                a[i,what,j:(j+value+1)] = 1

                A_ub = numpy.append(A_ub, [a], 0)
                b_ub = numpy.append(b_ub, [value], 0)
        else:
            return A_ub, b_ub, A_eq, b_eq

    return function

def personnel_count(what, when, req, opt=None):
    what = set_of_what(what)
    when = set_of_when(when)

    what = list(what)
    when = list(when)

    what,when = match_indices(what, when)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        for now in when:
            a = numpy.zeros_like(c)
            a[:,what,now] = 1

            if opt is not None:
                if req > 0:
                    A_ub = numpy.append(A_ub, [-a], 0)
                    b_ub = numpy.append(b_ub, [-req], 0)

                if opt > req:
                    A_ub = numpy.append(A_ub, [a], 0)
                    b_ub = numpy.append(b_ub, [opt], 0)
            else:
                A_eq = numpy.append(A_eq, [-a], 0)
                b_eq = numpy.append(b_eq, [-req], 0)
        else:
            return A_ub, b_ub, A_eq, b_eq

    return function

def total_hours(who, when, min, max):
    who = set_of_who(who)
    when = set_of_when(when)

    who = list(who)
    when = list(when)

    off = list(OFF_CONSOLE)
    on = list(ON_CONSOLE)

    when_off,off = match_indices(when, off)
    when_on,on = match_indices(when, on)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        for me in who:
            a = numpy.zeros_like(c)
            a[me,off,when_off] = 8
            a[me,on,when_on] = 12

            A_ub = numpy.append(A_ub, [a], 0)
            b_ub = numpy.append(b_ub, [max], 0)

            A_ub = numpy.append(A_ub, [-a], 0)
            b_ub = numpy.append(b_ub, [-min], 0)
        else:
            return A_ub, b_ub, A_eq, b_eq

    return function

def exclude_shift(who, what, when):
    who = set_of_who(who)
    what = set_of_what(what)
    when = set_of_when(when)

    who = list(who)
    when = list(when)
    what = list(what)

    what,who = match_indices(what, who)

    who = who * len(when)
    when,what = match_indices(when, what)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        a = numpy.zeros_like(c)
        a[who,what,when] = 1

        A_eq = numpy.append(A_eq, [a], 0)
        b_eq = numpy.append(b_eq, [0], 0)

        return A_ub, b_ub, A_eq, b_eq

    return function

def reserve_shift(who, what, when):
    who = set_of_who(who)
    what = set_of_what(what)
    when = set_of_when(when)

    who = list(who)
    when = list(when)
    what = list(what)

    what,who = match_indices(what, who)

    who *= len(when)
    when,what = match_indices(when, what)

    def function(c, A_ub, b_ub, A_eq, b_eq):
        a = numpy.zeros_like(c)
        a[who,what,when] = 1

        A_eq = numpy.append(A_eq, [a], 0)
        b_eq = numpy.append(b_eq, [len(when)], 0)

        return A_ub, b_ub, A_eq, b_eq

    return function

constraints = [
    singular_shift(ALL_SHIFTS),#Pauli exclusion principle

    #from On-Orbit Policy
    transition_shift(NIGHT_SHIFT, DAY_SHIFT | OFF_CONSOLE),#no back-to-backs
    consecutive_shifts(ON_CONSOLE, 7),#no more than 7 consecutive shifts
    personnel_count(DAY_SHIFT, WEEKDAY, 1),#one on weekday day shifts
    personnel_count(DAY_SHIFT, WEEKEND, 2),#two on weekend day shifts
    personnel_count(NIGHT_SHIFT, EVERYDAY, 2),#two on night shifts

    #from Two Person Ops Requirements
    personnel_count(SHIFT_LEAD & DAY_SHIFT, EVERYDAY, 1),
    personnel_count(SHIFT_LEAD & NIGHT_SHIFT, EVERYDAY, 1),

    #maximum of 5 off-consoles per weekday
    personnel_count(OFF_CONSOLE, WEEKDAY, 0, 5),
    personnel_count(OFF_CONSOLE, WEEKEND, 0),

    #cerfication restrictions
    exclude_shift(ALL_OPS_ENGS, OFF_CONSOLE | NIGHT_SHIFT, WEEKDAY),
    exclude_shift(ALL_OPS_ENGS, ALL_SHIFTS, WEEKEND),
    exclude_shift(ALL_SATCONS, SHIFT_LEAD, EVERYDAY),
]

#Repetition planning
constraints += [
    reserve_shift("A", DAY_SHIFT & SHIFT_LEAD, MONDAY & (WEEK[0] | WEEK[2])),
    reserve_shift("B", DAY_SHIFT & SHIFT_LEAD, TUESDAY & (WEEK[1] | WEEK[3])),
    reserve_shift("C", DAY_SHIFT & SHIFT_LEAD, WEDNESDAY & (WEEK[0] | WEEK[2])),
    reserve_shift("D", DAY_SHIFT & SHIFT_LEAD, THURSDAY & (WEEK[1] | WEEK[3]))
]

#Operations engineers
constraints += [
    total_hours(name, week, 12, 12)
    if i % 2 == j % 2 else
    total_hours(name, week, 0, 0)
    for i, name in enumerate(ALL_OPS_ENGS)
    for j, week in enumerate(WEEK)
]

#Satellite controllers
constraints += [
    total_hours(name, week, 0, 48)
    for name in ALL_SHIFT_LEADS | ALL_SATCONS
    for week in WEEK
]

def main():
    c = numpy.zeros((len(flight_ops), len(ALL_SHIFTS), time_frame))
    c = numpy.zeros_like(c, dtype=int)

    A_ub = numpy.zeros((0,)+c.shape)
    b_ub = numpy.zeros((0,))

    A_eq = numpy.zeros((0,)+c.shape)
    b_eq = numpy.zeros((0,))

    off = list(OFF_CONSOLE)
    on = list(ON_CONSOLE)

    c[:,off,:] = 8
    c[:,on,:] = 12

    for constraint in constraints:
        A_ub, b_ub, A_eq, b_eq = constraint(c, A_ub, b_ub, A_eq, b_eq)

    print A_ub.shape, A_eq.shape

    result = linprog(c.reshape((c.shape[0]*c.shape[1]*c.shape[2],)),
                     A_ub.reshape((A_ub.shape[0],
                                   A_ub.shape[1]*A_ub.shape[2]*A_ub.shape[3],)),
                     b_ub,
                     A_eq.reshape((A_eq.shape[0],
                                   A_eq.shape[1]*A_eq.shape[2]*A_eq.shape[3],)),
                     b_eq,
                     bounds=(0,1),
                     options={"disp":True,
                              "maxiter":4000,
                              "tol":0.1})

    x = numpy.round(result.x, 0)\
             .reshape(c.shape)\
             .astype(int)

    with open('test.csv', 'wb') as spreadsheet:
        writer = csv.writer(spreadsheet)

        o = list(OFF_CONSOLE)
        D = list(DAY_SHIFT)
        N = list(NIGHT_SHIFT)

        writer.writerow(["Name"] + date_range)
        for i in list(EVERYBODY):
            for name in flight_ops:
                if i in flight_ops[name]:
                    break

            writer.writerow([name] + ["o" if x[i,o,j].any() else \
                                      "D" if x[i,D,j].any() else \
                                      "N" if x[i,N,j].any() else \
                                      ""
                                      for j in range(x.shape[2])])

    return x

if __name__ == "__main__":
    main()