#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   13 Mar 2014

TBD.

Classes:
Processor -- TBD
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
from datetime import timedelta
from Queue import PriorityQueue

#External libraries
from zmq.eventloop import ioloop
from network import DiGraph

#Internal libraries
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
__version__ = "1.0"#current version [major.minor]

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
        
        obj = graph.node[node]["obj"]
        
        assert isinstance(obj,)
        
        mode = obj._routine.send() \
               if isinstance(obj,PrimeObject) else \
               mode
        
        for source,target,data in graph.out_edges_iter(node,data=True):
            assert isinstance(source,types.StringTypes)
            assert isinstance(target,types.StringTypes)
            
            assert source == node
            assert graph.has_node(target)
            
            if data.get("mode") is mode:
                sub = graph.node[target].get("obj")
                
                assert isinstance(sub,)
                
                if issubclass(sub,BehaviorObject):
                    graph,target = sub.super.graph,sub.name \
                                   if sub.graph is graph else \
                                   graph,sub.__name__
                
                assert isinstance(graph,DiGraph)
            
                self._schedule(graph,target,mode,priority=MEDIUM)
        