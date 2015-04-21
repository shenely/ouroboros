#!/usr/bin/env python2.7

"""Behavior objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   08 February 2015

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
"""


##################
# Import section #
#
#Built-in libraries
import pickle

#External libraries
from networkx import DiGraph

#Internal libraries
from common import *
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
__version__ = "2.0"#current version [major.minor]

DEFAULT_DOCUMENT = dict(story=dict(),
                        faces=dict(data=dict(require=list(),
                                             provide=list()),
                                   control=dict(input=list(),
                                                output=list())),
                        nodes=[ ],
                        edges=dict(data=list(),control=list()))
#
####################


def behavior(name,type,
             story=DEFAULT_DOCUMENT["story"],
             faces=DEFAULT_DOCUMENT["faces"],
             nodes=DEFAULT_DOCUMENT["nodes"],
             edges=DEFAULT_DOCUMENT["edges"]):
    def decorator(cls):
        cls.doc = dict(name=name,
                       type=type,
                       faces=faces,
                       nodes=nodes,
                       edges=edges)
        
        return cls
    
    return decorator

@behavior(name="BehaviorObject",
          type=None)
class BehaviorObject(BaseObject):
    """Generic behavior object"""
    
    @classmethod
    def install(cls,service):
        cls.doc["path"] = pickle.dumps(cls)
        
        service.set(cls.doc)
    
    def __init__(self,name,*arg,**kwargs):
        self.name = name
        
        self._data_graph = DiGraph()
        self._control_graph = DiGraph()
        
    def _update(self,*args,**kwargs):
        for key in kwargs:
            value = kwargs[key]
            
            self._data_graph.node[key]["obj"].value = value
    
    def set_required_data(self):pass
    def get_provided_data(self):pass
    
    def recv_input_control(self):pass
    def send_output_control(self):pass

@behavior(name="PrimitiveBehavior",
          type="BehaviorObject")
class PrimitiveBehavior(BehaviorObject):
    """Primitive (simple) behavior"""

@behavior(name="CompositeBehavior",
          type="BehaviorObject")
class CompositeBehavior(BehaviorObject):
    """Composite (complex) behavior"""