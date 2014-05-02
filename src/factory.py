#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   01 May 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-04-23    shenely         1.0         Initial revision
2014-05-01    shenely         1.1         Modified the way control is
                                            passed to the parent

"""


##################
# Import section #
#
#Built-in libraries
import pickle

#External libraries
from network import DiGraph

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = ["BehaviorFactory"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
#
####################

class BehaviorFactory(type):
    def __new__(meta,app,name):
        if name in app.classes:
            cls = app.classes.get(name)
        else:
            doc = app.behaviors.find_one({ name: name })
            
            base = pickle.loads(doc.path)
            
            cls = super(BehaviorFactory,meta).__new__(name,
                                                      (base,),
                                                      {app: app, doc: doc})
            
            app.classes[name] = cls
        
        return cls
              
    def __call__(cls,*args,**kwargs):
        data = DiGraph()
        control = DiGraph()
        
        for node in cls.doc.nodes:
            obj = BehaviorFactory\
                  (cls.app,node.type) \
                  (name=node.name,pins=node.pins,parent=control)
                  
            data.add_node((node,None),node=obj,type=None)
            control.add_node(node,node=obj)
            
            for n,d in obj.data.nodes_iter(data=True):
                if d.get("type") is not None and n[1] is None:
                    data.add_node((obj.name,n[0]),
                                  node=d.get("node"),
                                  type=None)
        else:
            control.add_node(cls.__name__,node=None)
            
        for link in cls.doc.links:
            data.add_edge((link.source.node,link.source.pin),
                          (link.target.node,link.target.pin))
        
        for pin in cls.doc.pins:
            data.node[(pin.name,None)]["type"] = pin.type
        
        for rule in cls.doc.rules:
            context = rule.target
            
            for action in rule.actions[::-1]:
                if context is not None:
                    control.add_edge(action,context,mode=Ellipsis)
                
                context = action
            
            for condition in rule.conditions[::-1]:
                if context is not None:
                    control.add_edge(condition.node,context,
                                     mode=condition.mode)
                
                context = condition.node
            
            for event in rule.events[::-1]:
                if context is not None:
                    control.add_edge(event,context,mode=Ellipsis)
                
                context = event
                
            if context is not None:
                if rule.source is not None:
                    control.add_edge(rule.source,context,mode=Ellipsis)
                  
        self = super(BehaviorFactory,cls).__call__(data=data,
                                                   control=control,
                                                   *args,**kwargs)
        
        setattr(control.node[cls.__name__],"node",self)
        
        return self