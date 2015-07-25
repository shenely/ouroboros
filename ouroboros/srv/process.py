#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   24 July 2015

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
2015-07-24    shenely         1.10        Removed socket support

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
import logging

#External libraries
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
__version__ = "1.10"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

#Priority/severity (log) scale
CRITICAL = 1
HIGH    =  10
MEDIUM  =  100
LOW     =  1000
TRIVIAL =  10000
#
####################


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
    _main = None        #main function
    #_env = simpy.RealtimeEnvironment()
    _env = simpy.Environment()
                
    def start(self):
        """Start the event loop."""
        if super(ProcessorService,self).start():
            self._start = self._env.event()
            self.resume()
            
            return True
        else:
            return False
        
    def stop(self):
        """Stop the event loop."""
        if super(ProcessorService,self).stop():
            self.pause()
            
            return True
        else:
            return False
            
    def pause(self):
        """Remove main function from event loop."""
        if super(ProcessorService,self).pause():
            self._pause.succeed()
            
            return True
        else:
            return False
                        
    def resume(self):
        """Inject main function into event loop."""
        if super(ProcessorService,self).resume():
            self._pause = self._env.event()
            self._start.succeed()
            
            self.run()
            
            return True
        else:
            return False
        
    def run(self):
        """"""
        if self._running:
            self._env.run(self._pause)
        else:
            self.resume()
            
    def schedule(self,root,path,trigger):
        def process():
            try:
                yield trigger
            except:
                return
            
            node,face = (path,None) \
                  if root._control_graph.has_node(path) else \
                  (path[:-1],path[-1])
            
            with root._control_graph.node[node].get("obj") as behavior:
                events = {mode:self._env.event() \
                          for mode in behavior._output_control}
                
                for source,target,data in root._control_graph.out_edges_iter(node,data=True):
                    if source == node and \
                       root._control_graph.node[target]["obj"] is not None:
                        self.schedule(root,target,events[data["mode"]])
                
                yield behavior.watch(self,root,node,*behavior._required_data)
                
                face = behavior(face)
                
                yield behavior.watch(self,root,node,*behavior._provided_data)
                
                for key in events.keys():
                    if key != face:
                        events[key].fail(Exception)
                else:
                    if face is not None:
                        events[face].succeed()
            
        return self._env.process(process())