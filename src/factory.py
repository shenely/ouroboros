#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   23 Apr 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-04-23    shenely         1.0         Initial revision

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
__version__ = "1.0"#current version [major.minor]
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
                  (name=node.name,pins=node.pins,parent=cls)
                  
            data.add_node((node,None),obj=obj,type=None)
            control.add_node(node,obj=obj)
            
            for n,d in obj.data.nodes_iter(data=True):
                if d.get("type") is not None and n[1] is None:
                    data.add_node((obj.name,n[0]),
                                  obj=d.get("obj"),
                                  type=None)
        else:
            control.add_node(cls.__name__,obj=cls)
            
        for link in cls.doc.links:
            data.add_edge((link.source.node,link.source.pin),
                          (link.target.node,link.target.pin))
        
        for pin in cls.doc.pins:
            data.node[(pin.name,None)]["type"] = pin.type
        
        for rule in cls.doc.rules:
            context = rule.source
            
            for event in rule.events:
                if context is not None:
                    control.add_edge(context,event,mode=Ellipsis)
                
                context = event
            
            for condition in rule.conditions:
                if context is not None:
                    control.add_edge(context,condition.node,
                                     mode=condition.mode)
                
                context = condition.node
            
            for action in rule.actions:
                if context is not None:
                    control.add_edge(context,action,mode=Ellipsis)
                
                context = action
                
            if context is not None:
                control.add_edge(context,rule.target,mode=None)
                  
        return super(BehaviorFactory,cls).__call__(data=data,
                                                   control=control,
                                                   *args,**kwargs)