#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 October 2014

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

"""


##################
# Import section #
#
#Built-in libraries
import types
from datetime import timedelta
from Queue import PriorityQueue

#External libraries
from zmq.eventloop import ioloop
from networkx import DiGraph

#Internal libraries
from behavior import *
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
__version__ = "1.7"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

#Priority/severity (log) scale
CRITICAL = 1
HIGH    =  10
MEDIUM  =  100
LOW     =  1000
TRIVIAL =  10000
#
####################


class ProcessorService(ServiceObject):
    _loop = ioloop.IOLoop.instance()#event loop
    _main = None                    #main function
    _queue = PriorityQueue()        #process queue
                
    def start(self):
        """Start the event loop."""
        if super(ProcessorService,self).start():
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
            self._main = self._loop.add_callback(self._main) \
                         if self._main is not None else \
                         None
            
            return True
        else:
            return False
                        
    def resume(self):
        """Inject main function into event loop."""
        if super(ProcessorService,self).resume():
            self._main = self._loop.add_callback(self.run)
            
            return True
        else:
            return False
        
    def run(self):
        """"""
        if self._running:
            while not self._queue.empty():
                self._dispatch()
            else:
                self.pause()
        else:
            self.resume()
        
    def schedule(self,graph,node,mode=Ellipsis,priority=MEDIUM):
        """Schedule a process for execution."""
        assert isinstance(graph,DiGraph)
        assert isinstance(node,types.StringTypes)
        assert graph.has_node(node)
        
        self._queue.put((priority,graph,node,mode))
        
        self.resume()
        
    def _dispatch(self):
        """Execute process and schedule"""
        priority,graph,node,mode = self._queue.get()
        
        assert isinstance(graph,DiGraph)
        assert isinstance(node,types.StringTypes)
        
        assert graph.has_node(node)
        
        behavior = graph.node[node].get("node")
        
        assert isinstance(behavior,BehaviorObject)
        
        #NOTE:  Composite behavior mode (shenely, 2014-04-30)
        # The assumption is that output-generating composite behaviors
        #   will feature a target behavior that will set the mode the
        #   behavior has transitioned into.
        mode = behavior() \
               if isinstance(behavior,PrimitiveBehavior) else \
               Ellipsis \
               if graph is not behavior._control else \
               mode# bubbles up through composite behaviors
        
        if isinstance(behavior,CompositeBehavior):
            #NOTE:  Processor directives (shenely, 2014-06-07)
            # In order to control flow between various levels of
            #   behaviors, each control graph contains two (2) copies
            #   of the behavior owning it:
            #    1. Source node as start point; control to children
            #    2. Target node as end point; control to parent
            graph,node = (behavior._super._control,behavior._name) \
                         if graph is behavior._control else \
                         (behavior._control,behavior.__class__.__name__)
        
        for source,target,data in graph.out_edges_iter(node,data=True):
            assert isinstance(source,types.StringTypes)
            assert isinstance(target,types.StringTypes)
            
            assert source == node
            assert graph.has_node(target)
            
            if data.get("mode") is mode:
                node = target
            
                #NOTE:  Execution priority (shenely, 2014-04-30)
                # Priority of execution is inherited from the
                #   previously executed behavior in a rule.  Typically,
                #   priority is determined when the rule is injected
                #   into the processor (but not exclusively so).  
                self.schedule(graph,node,mode,priority=priority)
        