#!/usr/bin/env python2.7

"""I don't know what this is yet

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   13 Mar 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import types
import uuid
import pickle

#External libraries
from network import DiGraph

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = []
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class BaseObject(object):pass

class BehaviorObject(BaseObject):
    def __init__(self,name,**pins):
        super(BehaviorObject,self).__init__()
        
        self.name = name
        
        for key in pins:
            value = pins[key]
            setattr(self,key,value)
            
    def __getitem__(self,name):
        node = self.data.node[(name,None)]
        
        if node is None:
            raise Exception#does not exist
        elif node.get("type") != "provided":
            raise Exception#is not provided
        else:
            return node.get("obj")
            
    def __setitem__(self,name,value):
        node = self.data.node[name]
        
        if node is None:
            raise Exception#does not exist
        elif node.get("type") != "required":
            raise Exception#is not required
        else:
            node["obj"] = value

class PrimitiveBehavior(BehaviorObject):
    def __init__(self,name,**pins):
        super(BehaviorObject,self).__init__(name,**pins)
                    
        self.data = DiGraph()
        self.control = DiGraph()
        
        for node in self.doc.nodes:
            obj = BehaviorMetaclass\
                  (self.app,self.app.behaviors.find_one(node.type)) \
                  (name=node.name,
                   **dict([(pin.name,pin.value) \
                           for pin in node.pins]))
                  
            self.data.add_node((node,None),obj=obj,type=None)
            self.control.add_node(node,obj=obj)
            
            for name,data in obj.data.nodes_iter(data=True):
                if data.get("type") is not None and name[1] is None:
                    obj.data.add_node((obj.name,name[0]),
                                      obj=data.get("obj"),type=None)
        else:
            self.control.add_node(cls.doc.name,obj=self)
            
        for link in cls.doc.links:
            self.data.add_edge((link.source.node,link.source.pin),
                               (link.target.node,link.target.pin))
        
        for pin in cls.doc.pins:
            self.data.node[(pin.name,None)]["type"] = pin.type

class CompositeBehavior(BehaviorObject):
    def __call__(self):
        for name,data in self.control.successors_iter(self.__name__,data=True):pass

class BehaviorMetaclass(type):
    def __new__(meta,app,doc):
        cls = pickle.loads(doc.path) \
              if doc.path is not None else \
              super(BehaviorMetaclass,meta).__new__(doc.name,
                                                    (CompositeBehavior,),
                                                    {doc: doc, app: app})
        
        return cls
              
    def __call__(cls,name,**pins):
        self = super(BehaviorMetaclass,cls).__call__(cls)
        
        self.name = name
        
        for key in pins:
            value = pins[key]
            setattr(self,key,value)
                    
        self.data = DiGraph()
        self.control = DiGraph()
        
        for node in self.doc.nodes:
            obj = BehaviorMetaclass\
                  (self.app,self.app.behaviors.find_one(node.type)) \
                  (name=node.name,
                   **dict([(pin.name,pin.value) \
                           for pin in node.pins]))
                  
            self.data.add_node((node,None),obj=obj,type=None)
            self.control.add_node(node,obj=obj)
            
            for name,data in obj.data.nodes_iter(data=True):
                if data.get("type") is not None and name[1] is None:
                    obj.data.add_node((obj.name,name[0]),
                                      obj=data.get("obj"),type=None)
        else:
            self.control.add_node(cls.doc.name,obj=self)
            
        for link in cls.doc.links:
            self.data.add_edge((link.source.node,link.source.pin),
                               (link.target.node,link.target.pin))
        
        for pin in cls.doc.pins:
            self.data.node[(pin.name,None)]["type"] = pin.type
        
        for rule in cls.doc.rules:
            context = rule.source
            
            for event in rule.events:
                if context is not None:
                    self.control.add_edge(context,event,mode=Ellipsis)
                
                context = event
            
            for condition in rule.conditions:
                if context is not None:
                    self.control.add_edge(context,condition.node,
                                          mode=condition.mode)
                
                context = condition.node
            
            for action in rule.actions:
                if context is not None:
                    self.control.add_edge(context,action,mode=Ellipsis)
                
                context = action
                
            if context is not None:
                self.control.add_edge(context,rule.target,mode=None)
                  
        return self