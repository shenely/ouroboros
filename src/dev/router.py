#!/usr/bin/env python2.7

"""Router devices

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 June 2014

TBD.

Classes:
RouterDevice  -- TBD
ThreadRouter  -- TBD
ProcessRouter -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-06-26    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from threading import Thread
from multiprocessing import Process

#External libraries
import zmq

#Internal libraries
#
##################


##################
# Export section #
#
__all__ = ["RouterDevice",
           "ThreadRouter",
           "ProcessRouter"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class RouterDevice(object):
    context_factory = None
    
    def __init__(self):
        context = self.context_factory()
         
        self._socket = context.socket(zmq.ROUTER)
        self._poller = zmq.Poller()
        
        self.daemon = True
    
    def bind(self,addr):
        self._socket.bind(addr)

    def connect(self,addr):
        self._socket.connect(addr)

    def join(self,timeout=None):
        self._poller.unregister(self._socket)

    def setsockopt(self,opt,value):
        self._socket.setsocketopt(opt,value)

    def start(self):
        self._poller.register(self._socket,zmq.POLLIN)
        
        self.run()
    
    def run(self):
        while True:
            sockets = dict(self._poller.poll())
            
            if (self._socket in sockets and sockets[self._socket] == zmq.POLLIN):
                source,target,message = self._socket.recv_multipart()
                
                self._socket.send_multipart((target,source,message))

class ThreadRouter(RouterDevice):
    context_factory = zmq.Context.instance
    
    def __init__(self):
        super(ThreadRouter,self).__init__()
        
        self._thread = Thread(target=self.run)
        
    def join(self,timeout=None):
        super(ThreadRouter,self).join(timeout)
        
        self._thread.join(timeout)
        
    def start(self):
        self._poller.register(self._socket,zmq.POLLIN)
        
        self._thread.daemon = self.daemon
        
        self._thread.start()

class ProcessRouter(RouterDevice):
    context_factory = zmq.Context
    
    def __init__(self):
        super(ProcessRouter,self).__init__()
        
        self._process = Process(target=self.run)
        
    def join(self,timeout=None):
        super(ProcessRouter,self).join(timeout)
        
        self._process.join(timeout)
        
    def start(self):
        self._poller.register(self._socket,zmq.POLLIN)
        
        self._process.daemon = self.daemon
        
        self._process.start()