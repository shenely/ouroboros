#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 September 2014

TBD.

Classes:
BehaviorFactory -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-04-23    shenely         1.0         Initial revision
2014-05-01    shenely         1.1         Modified the way control is
                                            passed to the parent
2014-06-11    shenely                     Added documentation
2014-08-18    shenely         1.2         Made 'friendly' with behavior
                                            objects
2014-09-10    shenely         1.3         Moving aways from metaclass


"""


##################
# Import section #
#
#Built-in libraries
import pickle

#External libraries
from networkx import DiGraph

#Internal libraries
#
##################=


##################
# Export section #
#
__all__ = ["behavior_factory",
           "BehaviorFactory"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]
#
####################


def behavior_factory(app,name):
        doc = app._database.get({ "name": name })# from database
            
        #NOTE:  Behavior initialization (shenely, 2014-06-11)
        # Behaviors for an application are created as subclasses of
        #   predefined behaviors at runtime.  This creates a common
        #   interface for injecting both primitive and composite
        #   behaviors into an application.  Behavior names are unique
        #   to an application.
        if name in app.classes:
            cls = app.classes.get(name)
        else:            
            cls = pickle.loads(doc.path)# import path for behavior
            
            app.classes[name] = cls
              
        def caller(*args,**kwargs):
            data = DiGraph()# data flow
            control = DiGraph()# control flow
            
            #Create behavior instances as graph nodes
            for node in doc.nodes:
                obj = behavior_factory\
                      (app,node.type) \
                      (name=node.name,pins=node.pins,graph=control)
                      
                data.add_node((node.name,None),node=obj,type=None,cls=app.classes[node.type])
                control.add_node(node.name,node=obj)
                
                #Expose provided and required nodes from child to parent
                for n,d in obj._data.nodes_iter(data=True):
                    if d.get("type") is not None and n[1] is None:
                        data.add_node((obj._name,n[0]),
                                      node=d.get("node"),
                                      type=None)
            else:
                control.add_node(cls.__name__,node=None)
                
            #Connect data interfaces with graph edges
            for link in doc.links:
                data.add_edge((link.source.node,link.source.pin),
                              (link.target.node,link.target.pin))
                
                source = data.node[link.source.node,link.source.pin]
                target = data.node[link.target.node,link.target.pin]
                
                target["node"].__del__()
                
                target["node"] = source["node"]
                
                if link.target.pin is not None:
                    child = data.node[link.target.node,None]
                    
                    target = child["node"]._data.node[link.target.pin,None]
                    other = child["node"]._control.node[link.target.pin]
                    
                    target["node"] = source["node"]
                    other["node"] = source["node"]
                    
            #Configure behavior data with predefined values
            for pin in doc.pins:
                data.node[(pin.node,None)]["type"] = pin.type
            
            #Connect control logic with graph edges
            for rule in doc.rules:
                context = rule.target# to clause
               
                for action in rule.actions[::-1]:# then clauses
                    if context is not None:
                        control.add_edge(action,context,mode=Ellipsis)
                    
                    context = action
                
                for condition in rule.conditions[::-1]:# given clauses
                    #NOTE:  Condition modes (shenely, 2014-06-10)
                    # Unlike other behavior types, the mode of conditions
                    #   is dependent upon the execution of the underlying
                    #   logic.  It is  the one type that allows for
                    #   branching.  Currently conditions only implement
                    #   boolean (i.e. True or False) values.  All other
                    #   types implement an Ellipsis as the singular mode.
                    if context is not None:
                        control.add_edge(condition.node,context,
                                         mode=condition.mode)
                    
                    context = condition.node
                
                for event in rule.events[::-1]:# when clauses
                    if context is not None:
                        control.add_edge(event,context,mode=Ellipsis)
                    
                    context = event
                    
                if context is not None:# from clause
                    if rule.source is not None:
                        control.add_edge(rule.source,context,mode=Ellipsis)
                      
            #Initialize the behavior with data and control graphs
            self = cls(data=data,control=control,*args,**kwargs)
            
            control.node[cls.__name__]["node"] = self
            
            return self
        
        return caller

class BehaviorFactory(type):
    def __new__(meta,app,name):
        #NOTE:  Behavior initialization (shenely, 2014-06-11)
        # Behaviors for an application are created as subclasses of
        #   predefined behaviors at runtime.  This creates a common
        #   interface for injecting both primitive and composite
        #   behaviors into an application.  Behavior names are unique
        #   to an application.
        if name in app.classes:
            cls = app.classes.get(name)
        else:
            doc = app._database.get({ "name": name })# from database
            
            base = pickle.loads(doc.path)# import path for behavior
            
            cls = super(BehaviorFactory,meta).__new__(meta,
                                                      str(name),(base,),
                                                      dict(_app=app, _doc=doc))
            
            app.classes[name] = cls
        
        return cls
    
    def __init__(self,app,name):
        super(BehaviorFactory,self).__init__(self)
              
    def __call__(cls,*args,**kwargs):
        data = DiGraph()# data flow
        control = DiGraph()# control flow
        
        #Create behavior instances as graph nodes
        for node in cls._doc.nodes:
            obj = BehaviorFactory\
                  (cls._app,node.type) \
                  (name=node.name,pins=node.pins,graph=control)
                  
            data.add_node((node.name,None),node=obj,type=None,cls=cls._app.classes[node.type])
            control.add_node(node.name,node=obj)
            
            #Expose provided and required nodes from child to parent
            for n,d in obj._data.nodes_iter(data=True):
                if d.get("type") is not None and n[1] is None:
                    data.add_node((obj._name,n[0]),
                                  node=d.get("node"),
                                  type=None)
        else:
            control.add_node(cls.__name__,node=None)
            
        #Connect data interfaces with graph edges
        for link in cls._doc.links:
            data.add_edge((link.source.node,link.source.pin),
                          (link.target.node,link.target.pin))
            
            source = data.node[link.source.node,link.source.pin]
            target = data.node[link.target.node,link.target.pin]
            
            target["node"].__del__()
            
            target["node"] = source["node"]
            
            if link.target.pin is not None:
                child = data.node[link.target.node,None]
                
                target = child["node"]._data.node[link.target.pin,None]
                other = child["node"]._control.node[link.target.pin]
                
                target["node"] = source["node"]
                other["node"] = source["node"]
                
        #Configure behavior data with predefined values
        for pin in cls._doc.pins:
            data.node[(pin.node,None)]["type"] = pin.type
        
        #Connect control logic with graph edges
        for rule in cls._doc.rules:
            context = rule.target# to clause
           
            for action in rule.actions[::-1]:# then clauses
                if context is not None:
                    control.add_edge(action,context,mode=Ellipsis)
                
                context = action
            
            for condition in rule.conditions[::-1]:# given clauses
                #NOTE:  Condition modes (shenely, 2014-06-10)
                # Unlike other behavior types, the mode of conditions
                #   is dependent upon the execution of the underlying
                #   logic.  It is  the one type that allows for
                #   branching.  Currently conditions only implement
                #   boolean (i.e. True or False) values.  All other
                #   types implement an Ellipsis as the singular mode.
                if context is not None:
                    control.add_edge(condition.node,context,
                                     mode=condition.mode)
                
                context = condition.node
            
            for event in rule.events[::-1]:# when clauses
                if context is not None:
                    control.add_edge(event,context,mode=Ellipsis)
                
                context = event
                
            if context is not None:# from clause
                if rule.source is not None:
                    control.add_edge(rule.source,context,mode=Ellipsis)
                  
        #Initialize the behavior with data and control graphs
        self = super(BehaviorFactory,cls).__call__(data=data,
                                                   control=control,
                                                   *args,**kwargs)
        
        control.node[cls.__name__]["node"] = self
        
        return self