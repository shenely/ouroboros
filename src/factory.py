#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 September 2014

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
2014-09-11    shenely         1.4         Removed metaclass


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
__all__ = ["behavior_factory"]
#
##################


####################
# Constant section #
#
__version__ = "1.4"#current version [major.minor]
#
####################


def behavior_factory(app,name):
        #NOTE:  Behavior initialization (shenely, 2014-09-11)
        # Behaviors for an application are created as instances of
        #   predefined behaviors at runtime.  This creates a common
        #   interface for injecting both primitive and composite
        #   behaviors into an application.  Behavior names are unique
        #   to an application.
        
        doc = app._database.get({ "name": name })# from database
        
        #Memoize classes if they've been loaded previously
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
                      
                #Add node to data and control graph
                data.add_node((node.name,None),
                              node=obj,type=None,
                              cls=app.classes[node.type])
                control.add_node(node.name,node=obj)
                
                #Expose provided and required nodes from child to parent
                for n,d in obj._data.nodes_iter(data=True):
                    if d.get("type") is not None and n[1] is None:
                        data.add_node((obj._name,n[0]),
                                      node=d.get("node"),
                                      type=None)
            else:
                control.add_node(cls.__name__,node=None)# placeholder
                
            #Connect data interfaces with graph edges
            for link in doc.links:
                data.add_edge((link.source.node,link.source.pin),
                              (link.target.node,link.target.pin))
                
                source = data.node[link.source.node,link.source.pin]
                target = data.node[link.target.node,link.target.pin]
                
                target["node"].__del__()# delete the target (always)
                target["node"] = source["node"]# replace with source (always)
                
                #Update any parent/child nodes (if applicable)
                if link.target.pin is not None:
                    child = data.node[link.target.node,None]
                    
                    target = child["node"]._data.node[link.target.pin,None]
                    other = child["node"]._control.node[link.target.pin]
                    
                    #Data is synchronized by reference
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
            
            #Behavior control contains a copy of itself
            control.node[cls.__name__]["node"] = self
            
            return self
        
        return caller