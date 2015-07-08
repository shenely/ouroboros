#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   04 June 2015

TBD.

Classes:
ProcessorService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision
2014-05-01    shenely         1.1         Integrated with new factory
                                            and behavior classes
2014-05-04    shenely         1.2         Renamed the main class
2014-05-06    shenely         1.3         Moved generic methods to a
                                            service object
2014-06-07    shenely                     Added documentation
2014-08-16    shenely         1.4         Made service 'friendly' to
                                            behaviors
2014-09-10    shenely         1.5         Properly create main loop
2014-09-12    shenely         1.6         Main loop was not being
                                            controlled properly
2014-10-15    shenely         1.7         Super is now behavior, not
                                            node
2015-04-20    shenely         1.8         Support for factory rewrite
2015-06-04    shenely         1.9         Added examine native method

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
from Queue import PriorityQueue
import logging

#External libraries
from zmq.eventloop import ioloop
from networkx import DiGraph
import simpy

#Internal libraries
from . import ServiceObject
#
##################


##################
# Export section #
#
__all__ = ["ProcessorService"]
#
##################


####################
# Constant section #
#
__version__ = "1.8"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

#Priority/severity (log) scale
CRITICAL = 1
HIGH    =  10
MEDIUM  =  100
LOW     =  1000
TRIVIAL =  10000
#
####################

ioloop.install()

def instruction(priority):
    def decorator(command):
        def function(self,event,graph,node):
            """Schedule a process for execution."""
            assert isinstance(graph,DiGraph)
            assert graph.has_node(node)
            
            gen = command(self,event,graph,node)
            
            return self._env.process(gen)
            
        return function
    
    return decorator

class ProcessorService(ServiceObject):
    _loop = ioloop.IOLoop.instance()#event loop
    _main = None                    #main function
    _queue = PriorityQueue()        #process queue
    #_env = simpy.RealtimeEnvironment()
    _env = simpy.Environment()
                
    def start(self):
        """Start the event loop."""
        if super(ProcessorService,self).start():
            self._loop.add_callback(self.resume)
            self._loop.start()
            
            return True
        else:
            return False
        
    def stop(self):
        """Stop the event loop."""
        if super(ProcessorService,self).stop():
            self._loop.stop()
            
            return True
        else:
            return False
            
    def pause(self):
        """Remove main function from event loop."""
        if super(ProcessorService,self).pause():
            self._dead.succeed()
            
            return True
        else:
            return False
                        
    def resume(self):
        """Inject main function into event loop."""
        if super(ProcessorService,self).resume():
            self._dead = self._env.event()
            
            self._loop.add_callback(self.run)
            
            return True
        else:
            return False
        
    def run(self):
        """"""
        if self._running:
            self._env.run(self._dead)
        else:
            self.resume()
            
    def schedule(self,thing,node,starter=None):
        node,face = (node,None) \
                    if thing._control_graph.has_node(node) else \
                    (node[:-1],node[-1])
                    
        if starter is None:
            starter = self._env.event()
            self._loop.add_callback(starter.succeed)
            
        ender = self._env.event()
        
        def process():
            yield starter
            
            with thing._control_graph.node[node].get("obj") as behavior:
                events = {mode:self._env.event() \
                          for mode in behavior._output_control}
                
                for source,target,data in thing._control_graph.out_edges_iter(node,data=True):
                    if source == node and \
                       thing._control_graph.node[target]["obj"] is not None:
                        self.schedule(thing,target,events[data["mode"]])
                
                yield self.watch(thing._data_graph,node,*behavior._required_data)
                
                face = behavior(face)
                
                yield self.watch(thing._data_graph,node,*behavior._provided_data)
            
                events[face].succeed()
            
            ender.succeed()
            
        self._env.process(process())
        
        return ender
    
    def listen(self,callback):
        def caller():
            self._env.process(callback())
            
        self._loop.add_callback(caller)
        
    def watch(self,graph,node,*faces):
        starter = self._env.event()
        self._loop.add_callback(starter.succeed)
        
        def looker():
            yield starter
            
            node_set = set()
            
            source = graph.node[node].get("obj")
            
            def recursion(e):
                node_set.add(e)
                
                for n in list(node_set):
                    for p in graph.predecessors_iter(n):
                        if p not in node_set:
                            recursion(p)
                    for s in graph.successors_iter(n):
                        if s not in node_set:
                            recursion(s)
            
            recursion(node)
            
            node_set.remove(node)
            
            for n in node_set:
                target = graph.node[n].get("obj")
                
                logging.debug("{0}:  Referenced to {1}".\
                              format(target.name,source.name))
                
                if hasattr(source,"value"):
                    if source.value is None and \
                       hasattr(target,"value"):
                        source.value = target.value
                        source.default = target.default
                        source.object_hook = target.object_hook
                    else:
                        target.value = source.value
                        target.default = source.default
                        target.object_hook = source.object_hook
                elif hasattr(target,"value") and \
                     target.value is not None:
                    source.value = target.value
                    source.default = target.default
                    source.object_hook = target.object_hook
        
        return self._env.process(looker())
        