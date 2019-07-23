# built-in libraries
import collections
import functools
import logging

# external libraries
import yaml

# internal libraries
from ouroboros.conf import CLOUD, STONE
from ouroboros.util import coroutine

# exports
__all__ = ("Type",
           "Event",
           "Item",
           "Mask", "Mode",
           "Node", "Edge", "Face",
           "Task",
           "Image",
           "run",)

# logging
logger = logging.getLogger(__name__)


class Type(collections.namedtuple
           ("Type", ("default", "object_hook"))):

    def __new__(cls, key, tag, type,
                default, object_hook):
        obj = super(Type, cls).__new__(cls, default, object_hook)
        yaml.add_constructor(tag, obj.constructor)
        STONE[key, type] = obj
        return obj

    def constructor(self, loader, node):
        if node.id == "scalar":
            obj = loader.construct_scalar(node)
        elif node.id == "sequence":
            obj = loader.construct_sequence(node)
        elif node.id == "mapping":
            obj = loader.construct_mapping(node)
        return self.object_hook(obj)


class Event(object):
    __slots__ = ("cbs",)

    def __init__(self, cbs=None):
        self.cbs = cbs or []


class Item(collections.namedtuple
           ("Item", ("data", "ctrl"))):

    def __new__(cls, data, ctrl):
        ctrl = {key: Event()
                for key in ctrl}
        return super(Item, cls).__new__(cls, data, ctrl)


class Mask(collections.namedtuple
           ("Mask", ("gets", "sets"))):
    pass


class Mode(collections.namedtuple
           ("Mode", ("data", "ctrl"))):

    def __new__(cls, ins, outs, reqs, pros):
        data = Mask(reqs, pros)
        ctrl = Mask(ins,  outs)
        return super(Mode, cls).__new__(cls, data, ctrl)


class Node(collections.namedtuple
           ("Node", ("init", "main"))):

    def __new__(cls, evs, args, ins, reqs, outs, pros):
        init = Mode(evs, (), args, ())
        main = Mode(ins, outs, reqs, pros)
        return super(Node, cls).__new__(cls, init, main)


class Edge(collections.namedtuple
           ("Edge", ("data", "ctrl"))):

    def __new__(cls, data=None, ctrl=None):
        data = data or {}
        ctrl = ctrl or {}
        return super(Edge, cls).__new__(cls, data, ctrl)


class Face(collections.namedtuple
           ("Face", ("data", "ctrl"))):

    def __new__(cls, node, edge, item):
        data = iterdata(node, edge, item)
        ctrl = iterctrl(node, edge, item)
        return super(Face, cls).__new__(cls, data, ctrl)


@coroutine
def iterdata(node, edge, item):
    """iterates over `init` and `main` data"""
    pros = yield

    # XXX takes advantage of there currently being no `data` provided
    # ... while in `init` mode
    mode = node.init
    if len(mode.data.gets) > 0:
        reqs = (logger.debug("get data: %s", key)
                or item.data.get(edge.data.get(key, key))
                for key in mode.data.gets)
        pros = yield reqs

    mode = node.main
    while True:
        if len(mode.data.gets) > 0:
            reqs = (logger.debug("get data: %s", key)
                    or item.data.get(edge.data.get(key, key))
                    for key in mode.data.gets)
            pros = yield reqs

        if len(mode.data.sets) > 0:
            item.data.update({edge.data.get(key, key):
                              logger.debug("set data: %s=%s", key, pro)
                              or pro
                              for key, pro
                              in zip(mode.data.sets, pros)
                              if pro is not None}
                             if pros is not None
                             else {})
            pros = yield


@coroutine
def iterctrl(node, edge, item):
    """iterates over `init` and `main` ctrl"""
    yield

    # XXX takes advantage of there currently being no `ctrl` output
    # ... while in `init` mode
    mode = node.init
    ins = (logger.debug("get ctrl: %s", key)
           or item.ctrl.get(edge.ctrl.get(key, key))
           for key in mode.ctrl.gets)
    outs = yield ins  # always called

    mode = node.main
    while True:
        if len(mode.ctrl.gets) > 0:
            ins = (logger.debug("get ctrl: %s", key)
                   or item.ctrl.get(edge.ctrl.get(key, key))
                   for key in mode.ctrl.gets)
            outs = yield ins

        if len(mode.ctrl.sets) > 0:
            evs = (((logger.debug("set ctrl: %s=%s", key, out)
                     or item.ctrl.get(edge.ctrl.get(key, key)), out)
                    for key, out in zip(mode.ctrl.sets, outs)
                    if out is not None)
                   if outs is not None
                   else ())
            outs = yield evs


class Task(collections.namedtuple
           ("Task", ("p", "gen"))):
    pass


class Image(object):
    __slots__ = ("tag", "nodes", "proc")

    def __init__(self, tag, **nodes):
        self.tag = tag
        self.nodes = nodes

    def __call__(self, func):
        func = coroutine(func)

        @coroutine
        @functools.wraps(func)
        def wrapper(**args):
            yield
            try:
                logger.debug("exec %s init", self.tag)
                gen = func(**args)  # create generator
                evs = yield
                while True:
                    logger.debug("exec %s main", self.tag)
                    yield gen.send(evs)
            except StopIteration:
                return
            finally:
                pass

        self.proc = wrapper
        CLOUD[self.tag] = self
        return wrapper


def run(task, model):
    img = CLOUD[task["tag"]]
    faces = {arg: Face((img.nodes[arg]
                        if arg in img.nodes
                        else img.nodes.get("kw")),
                       Edge(**task["maps"].get(arg, {})),
                       model[key])
             for (arg, key)
             in task["keys"].items()}
    gen = img.proc(**faces)
    obj = Task(task["p"], gen)
    any(ev.cbs.append(obj)
        for face in faces.values()
        for ev in next(face.ctrl) or ())
    return obj
