# built-in libraries
import collections
import functools
import logging

# external libraries
import yaml

# internal libraries
from ouroboros.config import CLOUD, STONE
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

    def __new__(cls, tag, type,
                default, object_hook):
        obj = super(Type, cls).__new__(cls, default, object_hook)
        yaml.add_constructor(tag, obj.constructor)
        STONE[tag, type] = obj
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
           ("Face", ("node", "edge", "item"))):

    @property
    def args(self):
        node, edge, item = self
        mode = node.init
        return (logger.debug("get data: %s", key)
                or item.data.get(edge.data.get(key, key))
                for key in mode.data.gets)

    @property
    def reqs(self):
        node, edge, item = self
        mode = node.main
        return (logger.debug("get data: %s", key)
                or item.data.get(edge.data.get(key, key))
                for key in mode.data.gets)

    @property
    def pros(self, pros):
        return NotImplemented
    
    @pros.setter
    def pros(self, pros):
        node, edge, item = self
        mode = node.main
        item.data.update({edge.data.get(key, key):
                          logger.debug("set data: %s=%s", key, pro)
                          or pro
                          for key, pro
                          in zip(mode.data.sets, pros)
                          if pro is not None})

    def evs(self):
        node, edge, item = self
        mode = node.init
        return (logger.debug("get ctrl: %s", key)
                or item.ctrl.get(edge.ctrl.get(key, key))
                for key in mode.ctrl.gets)

    def ins(self):
        node, edge, item = self
        mode = node.main
        return (logger.debug("get ctrl: %s", key)
                or item.ctrl.get(edge.ctrl.get(key, key))
                for key in mode.ctrl.gets)
        

    def outs(self, outs):
        node, edge, item = self
        mode = node.main
        return ((logger.debug("set ctrl: %s=%s", key, out)
                 or item.ctrl.get(edge.ctrl.get(key, key)), out)
                for key, out in zip(mode.ctrl.sets, outs)
                if out is not None)


class Task(collections.namedtuple
           ("Task", ("p", "tag", "gen"))):
    pass


class Image(object):
    __slots__ = ("tag", "nodes", "proc")

    def __init__(self, tag, **nodes):
        self.tag = tag
        self.nodes = nodes

    def __call__(self, func):
        coro = coroutine(func)
        self.proc = coro
        CLOUD[self.tag] = self
        return coro


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
    obj = Task(task["p"], img.tag, gen)
    any(ev.cbs.append(obj)
        for face in faces.values()
        for ev in face.evs())
