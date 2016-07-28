#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
BehaviorObject    -- TBD
PrimitiveBehavior -- TBD
CompositeBehavior -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision
2014-04-23    shenely         1.1         Finally figured out what to
                                            call this
2014-05-01    shenely         1.2         Removed ability to call
                                            execute composites, cleaned
                                            data update
2014-05-06    shenely         1.3         Moving away from getattr and
                                            setattr
2014-06-10    shenely         1.4         In composites, getattr and
                                            setattr were still being
                                            called
2014-06-11    shenely                     Added documentation
2014-08-18    shenely         1.5         Making all attributes private
                                            (ish)
2014-08-22    shenely         1.6         Combined behavior and structure
2014-09-10    shenely         1.7         Simplified data synchronization
2014-09-11    shenely         1.8         Organized behavior decorators
2014-10-15    shenely         1.9         Complete data synchronization
2014-10-22    shenely         1.10        Separating synchronization and
                                             tree traversal steps
2015-02-08    shenely         2.0         Complete rewrite
2015-07-01    shenely         2.1         Added uninstall method
2016-06-18    shenely         2.2         General code cleanup
"""


##################
# Import section #
#
#Built-in libraries
import pickle
import logging

#External libraries
from networkx import DiGraph
from bson import json_util

#Internal libraries
from .common import *
#
##################=


##################
# Export section #
#
__all__ = ["behavior",
           "BehaviorObject",
           "PrimitiveBehavior",
           "CompositeBehavior"]
#
##################


####################
# Constant section #
#
__version__ = "2.2"#current version [major.minor]

DEFAULT_DOCUMENT = {"story": {},
                    "faces": {"data":{"require":[],
                                      "provide":[]},
                              "control":{"input":[],
                                         "output":[]}},
                    "nodes":[],
                    "edges":{"data":[],"control":[]}}
#
####################


def behavior(**doc):
    def decorator(cls):
        cls.doc = doc
        
        return cls
    
    return decorator

@behavior(name="BehaviorObject",
          type=None)
class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    def __init__(self, name, *arg, **kwargs):
        self.name = name
        
        self._data_graph = DiGraph()
        self._control_graph = DiGraph()
        
    def init(self, *args, **kwargs):
        for key in kwargs:
            value = kwargs[key]
            
            self._data_graph.node[(key,)]["obj"].value = value

@behavior(name="PrimitiveBehavior",
          type="BehaviorObject")
class PrimitiveBehavior(BehaviorObject):
    """Primitive (simple) behavior"""
    
    def __call__(self, face):
        return NotImplemented
    
    def __getitem__(self, face):
        assert face in self._provided_data
        
        source = self._data_graph.node[(self.name, face)].get("obj")
        return source.value
    
    def __setitem__(self, face, value):
        assert face in self._required_data
        
        source = self._data_graph.node[(self.name, face)].get("obj")
        source.value = value
    
    def default(self, obj):
        return json_util.default(obj)
    
    def object_hook(self, dct):
        return json_util.object_hook(dct)

@behavior(name="CompositeBehavior",
          type="BehaviorObject")
class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""
    
    def __call__(self, face):
        assert face in self._input_control
        
        def recursion(path):
            for source, target in self._control_graph.out_edges_iter(path):
                node, face = target[:-1], target[-1]
                
                if self.__class__.__name__ in node:
                    return face
                else:
                    obj = self._data_graph.node[node]["obj"]
                    
                    self._update(*[node + (r,) for r in obj._required_data])
                    face = obj(face)
                    self._update(*[node + (p,) for p in obj._provided_data])
                    
                    path = node + (face,)
                    return recursion(path)
        
        path = (self.__class__.__name__, face)
        face = recursion(path)
        
        assert face in self._output_control
        return face
    
    def __getitem__(self, face):
        assert face in self._provided_data
        
        source = self._data_graph.node[(self.name, face)].get("obj")
        self._update((self.name, face))
        return source.value
    
    def __setitem__(self, face, value):
        assert face in self._required_data
        
        source = self._data_graph.node[(self.name, face)].get("obj")
        source.value = value
        self._update((self.name, face))
    
    def _update(self, *faces):
        for face in faces:
            nodes = set()
            
            source = self._data_graph.node[face].get("obj")
            
            def recursion(e):
                nodes.add(e)
                
                for n in list(nodes):
                    for p in self._data_graph.predecessors_iter(n):
                        if p not in nodes:
                            recursion(p)
                    for s in self._data_graph.successors_iter(n):
                        if s not in nodes:
                            recursion(s)
            
            recursion(face)
            nodes.remove(face)
            
            for n in nodes:
                target = self._data_graph.node[n].get("obj")
                
                logging.debug("{0}:  Referenced to {1}".\
                              format(".".join(face), ".".join(n)))
                
                if hasattr(source, "value"):
                    if source.value is None and \
                       hasattr(target, "value"):
                        source.value = target.value
                        source.default = target.default
                        source.object_hook = target.object_hook
                    else:
                        target.value = source.value
                        target.default = source.default
                        target.object_hook = source.object_hook
                elif hasattr(target, "value") and \
                     target.value is not None:
                    source.value = target.value
                    source.default = target.default
                    source.object_hook = target.object_hook