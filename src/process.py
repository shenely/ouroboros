#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   01 May 2014

TBD.

Classes:
Processor -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-03-13    shenely         1.0         Initial revision
2014-05-01    shenely         1.1         Integrated with new factory
                                            and behavior classes

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
from network import DiGraph

#Internal libraries
from factory import *
from behavior import *
#
##################=


##################
# Export section #
#
__all__ = ["Processor"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

CRITICAL = 1
HIGH    =  10
MEDIUM  =  100
LOW     =  1000
TRIVIAL =  10000
#
####################


class Processor(object):
    '''
    classdocs
    '''
    
    _self = None
    
    _queue = PriorityQueue()
    
    _started = False
    _running = False
    
    _main = None
    _loop = ioloop.IOLoop.instance()
    
    def __new__(cls):
        if cls._self is None:
            cls._self = object.__new__(cls)
            
        return cls._self

    def __init__(self):
        '''
        Constructor
        '''
                
    def start(self):
        if not self._started:
            self._started = True
            
            self._loop.start()
        
    def stop(self):
        if self._started:
            self._started = False
            
            self._loop.stop()
            
    def pause(self):
        if self._started and self._running:
            self._running = False
            
            self._main = self._loop.remove_timeout(self._main) \
                         if self._main is not None else \
                         None
                        
    def resume(self):
        if self._started and not self._running:
            self._running = True
            
            self._main = self._loop.add_timeout(TIMEOUT,self._run)
        
    def run(self):
        if self._r0unning:
            while not self._queue.empty():
                self._dispatch()
            else:
                self.pause()
        else:
            self.resume()
        
    def _schedule(self,graph,node,mode,priority=MEDIUM):
        assert isinstance(graph,DiGraph)
        assert isinstance(node,types.StringTypes)
        assert graph.has_node(node)
        
        self.queue.put((priority,graph,node,mode))
        
    def _dispatch(self):
        priority,graph,node,mode = self.queue.get()
        
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
               if graph is not behavior.control else \
               mode# bubbles up through composite behaviors
        
        if isinstance(behavior,CompositeBehavior):
            graph,node = behavior.super,behavior.name \
                         if graph is behavior.control else \
                         behavior.control,behavior.__class__.__name__
        
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
                self._schedule(graph,node,mode,priority=priority)
        