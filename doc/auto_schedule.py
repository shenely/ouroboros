__author__ = 'shenely'

import datetime
import csv
import types

import numpy
from scipy.optimize import linprog

start_date = datetime.date(2016,5,2)
time_frame = 14
flight_ops = [
    "Alice",
    "Bob",
    "Craig",
    "Eve",
    "Faythe",
    "Grace",
    "Mallory",
    "Oscar",
    "Peggy",
    "Sybil",
    "Victor",
    "Walter",
]

flight_ops = {flight_ops[i]: set((i,)) \
              for i in range(len(flight_ops))}

DAY = datetime.timedelta(days=1)

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

ALL_OPS_ENGS = flight_ops["Alice"] | \
                 flight_ops["Bob"] | \
                 flight_ops["Craig"] | \
                 flight_ops["Eve"]

ALL_SHIFT_LEADS = flight_ops["Faythe"] | \
                  flight_ops["Grace"] | \
                  flight_ops["Mallory"] | \
                  flight_ops["Oscar"]

ALL_SATCONS = flight_ops["Peggy"] | \
              flight_ops["Sybil"] | \
              flight_ops["Victor"] | \
              flight_ops["Walter"]

EVERYBODY = ALL_OPS_ENGS | ALL_SHIFT_LEADS | ALL_SATCONS

start_date -= DAY * start_date.weekday()
date_range = [start_date + i * DAY \
              for i in range(time_frame)]

MONDAY = set([i for i in range(len(date_range)) \
              if date_range[i].weekday() == 0])
TUESDAY = set([i for i in range(len(date_range)) \
               if date_range[i].weekday() == 1])
WEDNESDAY = set([i for i in range(len(date_range)) \
                 if date_range[i].weekday() == 2])
THURSDAY = set([i for i in range(len(date_range)) \
                if date_range[i].weekday() == 3])
FRIDAY = set([i for i in range(len(date_range)) \
              if date_range[i].weekday() == 4])
SATURDAY = set([i for i in range(len(date_range)) \
                if date_range[i].weekday() == 5])
SUNDAY = set([i for i in range(len(date_range)) \
              if date_range[i].weekday() == 6])

WEEKDAY = MONDAY | TUESDAY | WEDNESDAY | THURSDAY | FRIDAY
WEEKEND = SATURDAY | SUNDAY

EVERYDAY = WEEKDAY | WEEKEND

WEEK = [set(range(7*i,min(7*(i+1),len(date_range)))) \
        for i in range(len(date_range)/7)]

def set_of_who(who):
    return flight_ops[who] \
           if isinstance(who,types.StringTypes) and \
              who in flight_ops else\
           reduce(lambda a,b:a|b,
                  [flight_ops[me] \
                   for me in who \
                   if me in flight_ops]) \
           if isinstance(who,types.ListType) else \
           who \
           if isinstance(who,set) else \
           set()

def set_of_what(what):
    return what

def set_of_when(when):
    return [date_range.index(when)] \
           if isinstance(when,datetime.date) and \
              when in date_range else \
           set([date_range.index(now) \
                for now in when \
                if now in date_range]) \
           if isinstance(when,types.ListType) else \
           when \
           if isinstance(when,set) else \
           set()

def match_indices(self,other):
    other = other * len(self)
    self = sorted(self * (len(other) / len(self)))

    return self,other

def singular_shift(what):
    what = set_of_what(what)

    what = list(what)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]):
                a = numpy.zeros_like(c)
                a[i,what,j] = 1

                A_ub = numpy.append(A_ub,[a],0)
                b_ub = numpy.append(b_ub,[1],0)
        else:
            return A_ub,b_ub,A_eq,b_eq

    return function

def transition_shift(start,end,off=1):
    start = set_of_what(start)
    end = set_of_what(end)

    start = list(start)
    end = list(end)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]-off):
                a = numpy.zeros_like(c)
                a[i,start,j] = 1
                a[i,end,j+off] = 1

                A_ub = numpy.append(A_ub,[a],0)
                b_ub = numpy.append(b_ub,[1],0)
        else:
            return A_ub,b_ub,A_eq,b_eq

    return function

def consecutive_shifts(what,value):
    what = set_of_what(what)

    what = list(what)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for i in range(c.shape[0]):
            for j in range(c.shape[2]-value):
                a = numpy.zeros_like(c)
                a[i,what,j:(j+value+1)] = 1

                A_ub = numpy.append(A_ub,[a],0)
                b_ub = numpy.append(b_ub,[value],0)
        else:
            return A_ub,b_ub,A_eq,b_eq

    return function

def personnel_count(what,when,req,opt=None):
    what = set_of_what(what)
    when = set_of_when(when)

    what = list(what)
    when = list(when)

    what,when = match_indices(what,when)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for now in when:
            a = numpy.zeros_like(c)
            a[:,what,now] = 1

            if opt is not None:
                if req > 0:
                    A_ub = numpy.append(A_ub,[-a],0)
                    b_ub = numpy.append(b_ub,[-req],0)

                if opt > req:
                    A_ub = numpy.append(A_ub,[a],0)
                    b_ub = numpy.append(b_ub,[opt],0)
            else:
                A_eq = numpy.append(A_eq,[-a],0)
                b_eq = numpy.append(b_eq,[-req],0)
        else:
            return A_ub,b_ub,A_eq,b_eq

    return function

def total_hours(who,when,min,max):
    who = set_of_who(who)
    when = set_of_when(when)

    who = list(who)
    when = list(when)

    off = list(OFF_CONSOLE)
    on = list(ON_CONSOLE)

    when_off,off = match_indices(when,off)
    when_on,on = match_indices(when,on)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        for me in who:
            a = numpy.zeros_like(c)
            a[me,off,when_off] = 8
            a[me,on,when_on] = 12

            A_ub = numpy.append(A_ub,[a],0)
            b_ub = numpy.append(b_ub,[max],0)

            A_ub = numpy.append(A_ub,[-a],0)
            b_ub = numpy.append(b_ub,[-min],0)
        else:
            return A_ub,b_ub,A_eq,b_eq

    return function

def exclude_shift(who,what,when):
    who = set_of_who(who)
    what = set_of_what(what)
    when = set_of_when(when)

    who = list(who)
    when = list(when)
    what = list(what)

    what,who = match_indices(what,who)

    who = who * len(when)
    when,what = match_indices(when,what)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        a = numpy.zeros_like(c)
        a[who,what,when] = 1

        A_eq = numpy.append(A_eq,[a],0)
        b_eq = numpy.append(b_eq,[0],0)

        return A_ub,b_ub,A_eq,b_eq

    return function

def reserve_shift(who,what,when):
    who = set_of_who(who)
    what = set_of_what(what)
    when = set_of_when(when)

    who = list(who)
    when = list(when)
    what = list(what)

    what,who = match_indices(what,who)

    who *= len(when)
    when,what = match_indices(when,what)

    def function(c,A_ub,b_ub,A_eq,b_eq):
        a = numpy.zeros_like(c)
        a[who,what,when] = 1

        A_eq = numpy.append(A_eq,[a],0)
        b_eq = numpy.append(b_eq,[len(when)],0)

        return A_ub,b_ub,A_eq,b_eq

    return function

constraints = [
    singular_shift(ALL_SHIFTS),#Pauli exclusion principle

    #From On-Orbit Policy
    transition_shift(NIGHT_SHIFT, DAY_SHIFT | OFF_CONSOLE),#no back-to-backs
    consecutive_shifts(ON_CONSOLE, 7),#no more than 7 consecutive shifts
    personnel_count(DAY_SHIFT, WEEKDAY, 1),#a minimum of two certified
    personnel_count(DAY_SHIFT, WEEKEND, 2),#a minimum of two certified
    personnel_count(NIGHT_SHIFT, EVERYDAY, 2),#satellite controllers

    #From Two Person Ops Requirements
    personnel_count(SHIFT_LEAD & DAY_SHIFT, EVERYDAY, 1),
    personnel_count(SHIFT_LEAD & NIGHT_SHIFT, EVERYDAY, 1),

    #maximum of 5 off-console satellite controllers per weekday
    personnel_count(OFF_CONSOLE, WEEKDAY, 0, 5),
    personnel_count(OFF_CONSOLE, WEEKEND, 0),

    #Repetition planning
    reserve_shift("Alice", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,2)),
    #reserve_shift("Bob", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,3)),
    reserve_shift("Craig", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,4)),
    #reserve_shift("Eve", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,5)),

    #reserve_shift("Alice", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,9)),
    reserve_shift("Bob", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,10)),
    #reserve_shift("Craig", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,11)),
    reserve_shift("Eve", DAY_SHIFT & SHIFT_LEAD, datetime.date(2016,5,12)),

    #Operations engineers
    exclude_shift(ALL_OPS_ENGS, OFF_CONSOLE | NIGHT_SHIFT, WEEKDAY),
    exclude_shift(ALL_OPS_ENGS, ALL_SHIFTS, WEEKEND),
    total_hours("Alice", WEEK[0], 12, 12), total_hours("Alice", WEEK[1], 0, 0),
    total_hours("Bob", WEEK[0], 0, 0), total_hours("Bob", WEEK[1], 12, 12),
    total_hours("Craig", WEEK[0], 12, 12), total_hours("Craig", WEEK[1], 0, 0),
    total_hours("Eve", WEEK[0], 0, 0), total_hours("Eve", WEEK[1], 12, 12),

    #Shift leads
    total_hours("Faythe", WEEK[0], 36, 48), total_hours("Faythe", WEEK[1], 36, 48),
    total_hours("Grace", WEEK[0], 36, 48), total_hours("Grace", WEEK[1], 36, 48),
    total_hours("Mallory", WEEK[0], 36, 48), total_hours("Mallory", WEEK[1], 36, 48),
    total_hours("Oscar", WEEK[0], 36, 48), total_hours("Oscar", WEEK[1], 36, 48),

    #Satellite controllers
    exclude_shift(ALL_SATCONS,SHIFT_LEAD,EVERYDAY),
    total_hours("Peggy", WEEK[0], 36, 48), total_hours("Peggy", WEEK[1], 36, 48),
    total_hours("Sybil", WEEK[0], 36, 48), total_hours("Sybil", WEEK[1], 36, 48),
    total_hours("Victor", WEEK[0], 36, 48), total_hours("Victor", WEEK[1], 36, 48),
    total_hours("Walter", WEEK[0], 36, 48), total_hours("Walter", WEEK[1], 36, 48),
]

def main():
    c = numpy.zeros((len(flight_ops),len(ALL_SHIFTS),time_frame))
    c = numpy.zeros_like(c,dtype=int)

    A_ub = numpy.zeros((0,)+c.shape)
    b_ub = numpy.zeros((0,))

    A_eq = numpy.zeros((0,)+c.shape)
    b_eq = numpy.zeros((0,))

    off = list(OFF_CONSOLE)
    on = list(ON_CONSOLE)

    c[:,off,:] = 8
    c[:,on,:] = 12

    for constraint in constraints:
        A_ub,b_ub,A_eq,b_eq = constraint(c,A_ub,b_ub,A_eq,b_eq)

    print A_ub.shape,A_eq.shape

    result = linprog(c.reshape((c.shape[0]*c.shape[1]*c.shape[2],)),
                     A_ub.reshape((A_ub.shape[0],A_ub.shape[1]*A_ub.shape[2]*A_ub.shape[3],)),b_ub,
                     A_eq.reshape((A_eq.shape[0],A_eq.shape[1]*A_eq.shape[2]*A_eq.shape[3],)),b_eq,
                     bounds=(0,1),options={"disp":True,"maxiter":4000,"tol":0.1})

    x = numpy.round(result.x,0)\
             .reshape(c.shape)\
             .astype(int)

    with open('2016-05-02.csv', 'wb') as spreadsheet:
        writer = csv.writer(spreadsheet)

        o = list(OFF_CONSOLE)
        D = list(DAY_SHIFT)
        N = list(NIGHT_SHIFT)

        writer.writerow(["Name"] + [date.isoformat() for date in date_range])
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