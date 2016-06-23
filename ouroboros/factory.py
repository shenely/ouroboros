#!/usr/bin/env python2.7

"""Behavior factory

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

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
2014-09-12    shenely         1.5         Added event mixins
2014-09-15    shenely         1.6         Events are now listeners
2014-10-15    shenely         1.7         Creates custom composites
2015-04-20    shenely         2.0         Complete rewrite
2015-06-04    shenely         2.1         Passes args down to node
2015-07-24    shenely         2.2         Pass process instead of executive
2016-06-18    shenely         2.3         General code cleanup


"""


##################
# Import section #
#
#Built-in libraries
import pickle

#External libraries
from networkx import union, relabel_nodes

#Internal libraries
from .behavior import PrimitiveBehavior
from .lib.watch import WatcherPrimitive
from .lib.listen import ListenerPrimitive
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
__version__ = "2.3"#current version [major.minor]
#
####################

class BehaviorFactory(type):
    """Behavior factory"""
    
    def __new__(cls, app, name):        
        doc = app._database.get({"name": name})#from database
        #doc = app._database.get(name=name)#TODO:  Do it this way
        
        #Check if behavior has been memoized
        if name in app._memoized_classes:
            obj = app._memoized_classes[name]
        else:            
            obj = pickle.loads(doc.path)#import path for behavior
            
            #All behaviors are pushed through factory
            obj = super(BehaviorFactory, cls).__new__(cls, str(doc.name), (obj,),
                                                      {"app": app, "doc": doc})
            
            #Memoize behavior in application
            app._memoized_classes[name] = obj
                  
        return obj
    
    def __init__(self, app, name):
        #Data interfaces store the behavior classes only
        self._required_data = {data.name: BehaviorFactory(app, data.type)
                               for data in self.doc.faces.data.require}
        self._provided_data = {data.name: BehaviorFactory(app, data.type)
                               for data in self.doc.faces.data.provide}
            
        #Control interfaces do not have associated behaviors
        self._input_control = self.doc.faces.control.input
        self._output_control = self.doc.faces.control.output
        
    def __call__(self, name, top=True, *args, **kwargs):
        #Instantiate behaviors (should this really do anything?)
        obj = super(BehaviorFactory, self).__call__(name, *args, **kwargs)
        
        #Interfaces are defined via behavior classes, not instances
        for face in self._required_data:#required data interfaces
            obj._data_graph.add_node((obj.__class__.__name__, face),
                                     obj=self._required_data[face])
        for face in self._provided_data:#provided data interfaces
            obj._data_graph.add_node((obj.__class__.__name__, face),
                                     obj=self._provided_data[face])
        for face in self._input_control:#input control interfaces
            obj._control_graph.add_node((obj.__class__.__name__, face),
                                        obj=None)
        for face in self._output_control:#output control interfaces
            obj._control_graph.add_node((obj.__class__.__name__, face),
                                        obj=None)
        
        for node in self.doc.nodes:
            #Create each contained behaviors
            behavior = BehaviorFactory(self.app, node.type)\
                                      (node.name, False,
                                       **{arg.name: arg.value
                                          for arg in node.args})
            
            #Add contained behavior to current graphs (both data and control)
            obj._data_graph.add_node((node.name,), obj=behavior)
            obj._control_graph.add_node((node.name,), obj=behavior)
            
            #Add a depth of context to the contained behavior's graphs
            data_subgraph = relabel_nodes(behavior._data_graph,
                                          lambda x: (node.name,)+x)
            control_subgraph = relabel_nodes(behavior._control_graph,
                                             lambda x: (node.name,)+x)
            
            #Add the subgraphs to their respective graphs
            obj._data_graph = union(obj._data_graph, data_subgraph)
            obj._control_graph = union(obj._control_graph, control_subgraph)
            
            #Remove all interfaces inherited from the subgraphs
            for face in behavior._required_data:#required data interfaces
                obj._data_graph.remove_node((node.name,
                                             behavior.__class__.__name__,
                                             face))
            for face in behavior._provided_data:#provided data interfaces
                obj._data_graph.remove_node((node.name,
                                             behavior.__class__.__name__,
                                             face))
            for face in behavior._input_control:#input control interfaces
                obj._control_graph.remove_node((node.name,
                                                behavior.__class__.__name__,
                                                face))
            for face in behavior._output_control:#output control interfaces
                obj._control_graph.remove_node((node.name,
                                                behavior.__class__.__name__,
                                                face))
                
        #XXX:  Initialize variables *after* object creation
        obj.init(*args, **kwargs)
        
        if top:
            #Add watchers to the event loop
            for node, data in obj._data_graph.nodes_iter(data=True):
                if isinstance(data["obj"], WatcherPrimitive):
                    data["obj"].watch(self.app._process, obj, node,
                                      *data["obj"]._provided_data)
                    data["obj"].watch(self.app._process, obj, node,
                                      *data["obj"]._required_data)
            
            #Add listeners to the event loop
            for node, data in obj._control_graph.nodes_iter(data=True):
                if isinstance(data["obj"], ListenerPrimitive):
                    data["obj"].listen(self.app._process, obj,node)
            
        #Create new edges in data graph
        for edge in self.doc.edges.data:
            
            #Is source of the edge...
            if edge.source.node == obj.__class__.__name__:#...self?
                source_iter = iter([(edge.source.face,)])
            else:
                #Referenced nodes must exist in data graph
                assert obj._data_graph.has_node((edge.source.node,))
            
                if edge.source.face is not None:#...deep?
                    
                    #Get the 'shallow' node to the deep source
                    source_node = obj._data_graph.node[(edge.source.node,)]
                    source = source_node["obj"]
                    
                    #Source must be provided
                    assert edge.source.face in source._provided_data
                    
                    #Get all predecessors to provided interface in subgraph
                    source_iter = source._data_graph\
                                        .predecessors_iter((source.__class__.__name__,
                                                            edge.source.face))
                else:#...shallow?
                    #XXX:  Shallow edge reference hack (shenely, 2015-03-11)
                    #  This is only valid because the empty tuple created will be
                    #    concatenated with a tuple that references the context of
                    #    the shallow node.
                    source_iter = iter([()])
            
            #Is target of the edge...
            if edge.target.node == obj.__class__.__name__:#...self?
                target_iter = iter([(edge.target.face,)])
            else:
                #Referenced nodes must exist in data graph
                assert obj._data_graph.has_node((edge.target.node,))
            
                if edge.target.face is not None:#...deep?
                
                    #Get the 'shallow' node to the deep target
                    target_node = obj._data_graph.node[(edge.target.node,)]
                    target = target_node["obj"]
                    
                    #Source must be provided
                    assert edge.target.face in target._required_data
                    
                    #Get all successors to required interface in subgraph
                    target_iter = target._data_graph\
                                        .successors_iter((target.__class__.__name__,
                                                          edge.target.face))
                else:#...shallow?
                    #XXX:  Shallow edge reference hack (shenely, 2015-03-11)
                    #  This is only valid because the empty tuple created will be
                    #    concatenated with a tuple that references the context of
                    #    the shallow node.
                    target_iter = iter([()])
                
            for source_name in source_iter:
                #Extract source for some checks
                source = obj._data_graph.node\
                             [(edge.source.node,) + source_name]["obj"]
                    
                if isinstance(source, BehaviorFactory):
                    pass#an interface is being referenced
                elif isinstance(source, PrimitiveBehavior):
                    source = source.__class__#checks are made on classes
                else:
                    raise#cannot require/provide composite behaviors
                
                for target_name in target_iter:
                    #Extract target for some checks
                    target = obj._data_graph.node\
                                 [(edge.target.node,) + target_name]["obj"]
                    
                    if isinstance(target, BehaviorFactory):
                        pass#an interface is being referenced
                    elif isinstance(target, PrimitiveBehavior):
                        target = target.__class__# checks are made on classes
                    else:
                        raise#cannot require/provide composite behaviors
                             
                    #Confirm that target and source are somehow related
                    #XXX:  To account for the behavior factory metaclass
                    assert issubclass(target.__mro__[1],
                                      source.__mro__[1]) \
                        or issubclass(source.__mro__[1],
                                      target.__mro__[1])
                    
                    #Create data edge between source and target
                    obj._data_graph.add_edge((edge.source.node,) + source_name,
                                             (edge.target.node,) + target_name)
        
        #Create new edges in control graph
        for edge in self.doc.edges.control:
            
            if edge.source.node == obj.__class__.__name__:
                source_iter = iter([(edge.source.face,)])
                
                mode_iter = iter([edge.source.face,])
            else:
                #Referenced nodes must exist in control graph
                assert obj._control_graph.has_node((edge.source.node,))
                
                #Get the 'shallow' node to the deep source
                source_node = obj._control_graph.node[(edge.source.node,)]
                source = source_node["obj"]
                
                #Source must be an output
                assert edge.source.face in source._output_control
                
                #Get all predecessors to output interface in subgraph
                if isinstance(source,PrimitiveBehavior):
                    source_iter = iter([()])
                    
                    mode_iter = iter([edge.source.face,])
                else:
                    source_iter = source._control_graph\
                                        .predecessors((source.__class__.__name__,
                                                       edge.source.face))
                                        
                    mode_iter = iter([source._control_graph.edge[node]
                                                                [(source.__class__.__name__,
                                                                  edge.source.face)]
                                                                ["mode"]
                                      for node in source_iter])
            
            if edge.target.node == obj.__class__.__name__:
                target_iter = iter([(edge.target.face,)])
            else:
                #Referenced nodes must exist in control graph
                assert obj._control_graph.has_node((edge.target.node,))
                
                #Get the 'shallow' node to the deep target
                target_node = obj._control_graph.node[(edge.target.node,)]
                target = target_node["obj"]
                
                #Target must be an input
                assert edge.target.face in target._input_control
    
                #Get all successors to input interface in subgraph
                if isinstance(target,PrimitiveBehavior):
                    target_iter = iter([()])
                else:
                    target_iter = target._control_graph\
                                        .successors_iter((target.__class__.__name__,
                                                          edge.target.face))
                                    
            
            #TODO:  Mode origin (shenely, 2015-05-23)
            #  The mode must come from the source edge
            for source_name in source_iter:
                mode = mode_iter.next()
                for target_name in target_iter:
                    #Create control edge between source and target
                    obj._control_graph.add_edge((edge.source.node,) + source_name,
                                                (edge.target.node,) + target_name,
                                                mode=mode)
        
        return obj
        