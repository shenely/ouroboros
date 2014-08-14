#!/usr/bin/env python2.7

"""Messaging service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   20 June 2014

TBD.

Classes:
MessagingService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-06-20    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq
from zmq.devices import ThreadProxy

#Internal libraries
from . import ServiceObject
from device.router import ThreadRouter
#
##################


##################
# Export section #
#
__all__ = ["MessagingService"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class MessagingService(ServiceObject):
                
    def start(self):
        if super(MessagingService,self).start():
            self.proxy = ThreadProxy(zmq.PUB,zmq.SUB)
            self.router = ThreadRouter()
            
            return True
        else:
            return False
        
    def stop(self):
        if super(MessagingService,self).stop():
            self.proxy.join()
            self.router.join()
            
            return True
        else:
            return False
            
    def pause(self):
        if super(MessagingService,self).pause():
            #XXX:  Can devices really be paused? (shenely, 2014-06-16)
            return True
        else:
            return False
                        
    def resume(self):
        if super(MessagingService,self).resume():
            self.proxy.bind_in("tcp://127.0.0.1:5555")
            self.proxy.bind_out("tcp://127.0.0.1:5556")
            self.router.bind("tcp://127.0.0.1:5560")
            
            self.proxy.setsockopt_in(zmq.SUBSCRIBE,"")
    
            self.run()
            
            return True
        else:
            return False
            
    def run(self):
        if self._running:
            self.proxy.start()
            self.router.start()
        else:
            self.resume()