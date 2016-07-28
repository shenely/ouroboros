#!/usr/bin/env python2.7

"""Processor service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   23 June 2016

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
2016-06-22    shenely         1.11        Control flow via exception
2016-06-23    shenely         1.12        Undid last change

"""


##################
# Import section #
#
#Built-in libraries
import datetime
import logging

#External libraries
import tornado.ioloop

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
__version__ = "1.12"#current version [major.minor]

TIMEOUT = datetime.timedelta(0, 0, 0, 100)#time between running

#Priority/severity (log) scale
CRITICAL = 1
HIGH    =  10
MEDIUM  =  100
LOW     =  1000
TRIVIAL =  10000
#
####################


class ProcessorService(ServiceObject):
    _loop = tornado.ioloop.IOLoop.current()
                
    def start(self):
        """Start the event loop."""
        if super(ProcessorService, self).start():
            self.resume()
            
            return True
        else:
            return False
        
    def stop(self):
        """Stop the event loop."""
        if super(ProcessorService, self).stop():
            self.pause()
            
            return True
        else:
            return False
            
    def pause(self):
        """Remove main function from event loop."""
        if super(ProcessorService, self).pause():
            if self._running:
                self._loop.stop()
            
            return True
        else:
            return False
                        
    def resume(self):
        """Inject main function into event loop."""
        if super(ProcessorService, self).resume():
            self.run()
            
            return True
        else:
            return False
        
    def run(self):
        """"""
        if self._running:
            self._loop.start()
        else:
            self.resume()
            
    def schedule(self, root, path):
        def process():            
            node, face = (path, None) \
                         if root._control_graph.has_node(path) else \
                         (path[:-1], path[-1])
            
            with root._control_graph.node[node].get("obj") as behavior:                
                behavior.watch(self, root, node, *behavior._required_data)
                
                face = behavior(face)
                targets = [target for source, target, data
                           in root._control_graph.out_edges_iter(node,
                                                                 data=True)
                           if data["mode"] == face
                           and root._control_graph.node[target]["obj"]
                           is not None]
                for target in targets:self.schedule(root, target)
                
                behavior.watch(self, root, node, *behavior._provided_data)
            
        return self._loop.add_callback(process)