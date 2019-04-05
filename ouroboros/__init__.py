# built-in libraries
import collections
import functools
import itertools
import json
import logging

# external libraries
# ...

# internal libraries
# ...

# exports
__all__ = ("CLOUD", "ENCODE", "DECODE",
           "Event", "Item", "Task",
           "Mask" "Mode", "Node", "Edge", "Face")

# constants
CLOUD = {}  # task catelog

ENCODE = {}  # Python-to-JSON encoders
DECODE = {}  # JSON-to-Python decoders


def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.next()
        return gen
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    return wrapper


def default(obj):
    try:
        dct = next({key: default(obj)}
                   for (cls, (key, default)) in ENCODE.iteritems()
                   if isinstance(obj, cls))
        return dct
    except StopIteration:
        raise TypeError


def object_hook(dct):
    try:
        obj = next(DECODE.get(key)(value)
                   for (key, value) in dct.iteritems()
                   if key in DECODE)
        return obj
    except StopIteration:
        return dct


encoder = json.JSONEncoder(default=default)
decoder = json.JSONDecoder(object_hook=object_hook)


class Event(object):
    __slots__ = ("cbs",)

    def __init__(self, cbs=None):
        self.cbs = cbs or []


class Base(object):
    __slots__ = ("data", "ctrl")

    def __init__(self, data, ctrl):
        self.data = data
        self.ctrl = ctrl


class Item(Base):

    def __init__(self, data, ctrl):
        ctrl = {key: Event()
                for key in ctrl}
        return super(Item, self).__init__(data, ctrl)
        

class Mask(object):
    __slots__ = ("gets", "sets")

    def __init__(self, gets, sets):
        self.gets = gets
        self.sets = sets


class Mode(Base):

    def __init__(self, ins, outs, reqs, pros):
        data = Mask(reqs, pros)
        ctrl = Mask(ins,  outs)
        return super(Mode, self).__init__(data, ctrl)


class Node(object):
    __slots__ = ("init", "main")

    def __init__(self, evs, args, ins, reqs, outs, pros):
        self.init = Mode(evs, (), args, ())
        self.main = Mode(ins, outs, reqs, pros)


class Edge(Base):

    def __init__(self, data=None, ctrl=None):
        data = data or {}
        ctrl = ctrl or {}
        return super(Edge, self).__init__(data, ctrl)
        

class Face(Base):

    def __init__(self, node, edge, item):
        data = self.iterdata(node, edge, item)
        ctrl = self.iterctrl(node, edge, item)
        return super(Face, self).__init__(data, ctrl)

    @staticmethod
    @coroutine
    def iterdata(node, edge, item):
        pros = yield
        
        # XXX takes advantage of there currently being no `data` provided
        # ... while in `init` mode
        mode = node.init
        if len(mode.data.gets) > 0:
            reqs = (logging.debug("get data: %s", key)
                    or item.data.get(edge.data.get(key, key))
                    for key in mode.data.gets)
            pros = yield reqs
                    
        mode = node.main
        while True:
            if len(mode.data.gets) > 0:
                reqs = (logging.debug("get data: %s", key)
                        or item.data.get(edge.data.get(key, key))
                        for key in mode.data.gets)
                pros = yield reqs
            
            if len(mode.data.sets) > 0:
                item.data.update({edge.data.get(key, key):
                                  logging.debug("set data: %s=%s", key, pro)
                                  or pro
                                  for key, pro
                                  in itertools.izip(mode.data.sets, pros)
                                  if pro is not None}
                                 if pros is not None
                                 else {})
                pros = yield


    @staticmethod
    @coroutine
    def iterctrl(node, edge, item):
        yield
        
        # XXX takes advantage of there currently being no `ctrl` output
        # ... while in `init` mode
        mode = node.init
        ins = (logging.debug("get ctrl: %s", key)
               or item.ctrl.get(edge.ctrl.get(key, key))
               for key in mode.ctrl.gets)
        outs = yield ins  # always called
            
        mode = node.main
        while True:
            if len(mode.ctrl.gets) > 0:
                ins = (logging.debug("get ctrl: %s", key)
                       or item.ctrl.get(edge.ctrl.get(key, key))
                       for key in mode.ctrl.gets)
                outs = yield ins
            
            if len(mode.ctrl.sets) > 0:
                evs = (((logging.debug("set ctrl: %s=%s", key, out)
                         or item.ctrl.get(edge.ctrl.get(key, key)), out)
                        for key, out in itertools.izip(mode.ctrl.sets, outs)
                        if out is not None)
                       if outs is not None
                       else ())
                outs = yield evs

                
Task = collections.namedtuple("Task", ("p", "gen"))


class Image(object):

    def __init__(self, name, **nodes):
        self.name = name
        self.nodes = nodes

    def __call__(self, func):
        func = coroutine(func)
        @coroutine
        @functools.wraps(func)
        def wrapper(**args):
            yield
            try:
                logging.debug("exec %s init", self.name)
                gen = func(**args)# create generator
                evs = yield
                while True:
                    logging.debug("exec %s main", self.name)
                    yield gen.send(evs)
            except StopIteration:
                return
            finally:
                pass
        self.proc = wrapper
        CLOUD[self.name] = self
        return wrapper


def run(task, model):
    img = CLOUD[task["tag"]]
    faces = {arg: Face(node,
                       Edge(**task["maps"].get(arg, {})),
                       model[task["keys"][arg]])
             for (arg, node)
             in img.nodes.iteritems()}
    gen = img.proc(**faces)
    obj = Task(task["p"], gen)
    any(ev.cbs.append(obj)
        for face in faces.itervalues()
        for ev in face.ctrl.next() or ())
    return obj


