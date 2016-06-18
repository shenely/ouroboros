#!/usr/bin/env python2.7

"""Execution service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   24 July 2015

TBD.

Classes:
ExecutionService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-06    shenely         1.0         Initial revision
2014-06-11    shenely                     Added documentation
2014-09-10    shenely         1.1         Reorganized processor
2014-09-15    shenely         1.2         Added messaging service
2015-04-20    shenely         1.3         Support for factory rewrite
2015-07-24    shenely         1.4         Removed socket support

"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
from ..factory import BehaviorFactory
from . import ServiceObject
from .process import ProcessorService
from .persist import PersistenceService
#
##################=


##################
# Export section #
#
__all__ = ["ExecutionService"]
#
##################


####################
# Constant section #
#
__version__ = "1.4"#current version [major.minor]

#Default MongoDB settings
MONGO_HOST = "localhost"
MONGO_PORT = 27017

DATABASE_INSTANCE = "ouroboros"
BEHAVIOR_COLLECTION = "behaviors"

MAIN_NAME = "main"
# 
####################


class ExecutionService(ServiceObject):
    """Behavior execution service"""
    
    _memoized_classes = dict()
    
    def __init__(self,name):
        super(ExecutionService,self).__init__()
        
        self.name = name
        
        self._process = ProcessorService()
        self._database = PersistenceService()
    
    def start(self):
        """Connect to behavior database."""
        if super(ExecutionService,self).start():
            self._database.start()
            
            return True
        else:
            return False
            
    def stop(self):
        """Disconnect from behavior database."""
        if super(ExecutionService,self).stop():
            self._database.stop()
            
            return True
        else:
            return False
            
    def pause(self):
        """Pause the processing service."""
        if super(ExecutionService,self).pause():
            self._database.pause()
            
            self._process.stop()
            
            return True
        else:
            return False
            
    def resume(self):
        """Resume the processing service."""
        if super(ExecutionService,self).resume():
            self._database.resume()
            
            self.run()
            
            self._process.start()
            
            return True
        else:
            return False
            
    def run(self):
        """Initialize main behavior."""
        if self._running:
            self._main = BehaviorFactory(self,self.name)(MAIN_NAME)
        else:
            self.resume()