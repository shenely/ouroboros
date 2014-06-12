#!/usr/bin/env python2.7

"""Execution service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 June 2014

TBD.

Classes:
ExecutionService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-06    shenely         1.0         Initial revision
2014-06-11    shenely                     Added documentation

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
from pymongo import MongoClient

#Internal libraries
from common import ObjectDict
from service import ServiceObject
from factory import BehaviorFactory
from process import ProcessorService
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
__version__ = "1.0"#current version [major.minor]

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
    
    classes = dict()
    
    def __init__(self,name):
        self.name = name
        
        self._process = ProcessorService()
    
    def start(self):
        """Connect to behavior database."""
        if super(ExecutionService,self).start():
            self._process.start()
            
            self._client = MongoClient(MONGO_HOST,MONGO_PORT,document_class=ObjectDict)
            self._database = self._client[DATABASE_INSTANCE]
            self.behaviors = self._database[BEHAVIOR_COLLECTION]
            
            return True
        else:
            return False
            
    def stop(self):
        """Disconnect from behavior database."""
        if super(ExecutionService,self).stop():
            self._process.stop()
            
            self._database.logout()
            self._client.disconnect()
            
            return True
        else:
            return False
            
    def pause(self):
        """Pause the processing service."""
        if super(ExecutionService,self).pause():
            self._process.pause()
            
            return True
        else:
            return False
            
    def resume(self):
        """Resume the processing service."""
        if super(ExecutionService,self).resume():
            self.run()
            
            self._process.resume()
            
            return True
        else:
            return False
            
    def run(self):
        """Initialize main behavior."""
        if self._running:
            self._main = BehaviorFactory(self,self.name)(name=MAIN_NAME)
            self._process.schedule(self._main.control,self._main.name,Ellipsis)
        else:
            self.resume()