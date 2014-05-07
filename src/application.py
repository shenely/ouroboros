#!/usr/bin/env python2.7

"""Application service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 May 2014

TBD.

Classes:
ApplicationService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-06    shenely         1.0         Initial revision

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
__all__ = []
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

HOST_NAME = "localhost"
PORT_NUMBER = 27017

DATABASE_INSTANCE = "ouroboros"
BEHAVIOR_COLLECTION = "behaviors"

MAIN_NAME = "main"
# 
####################


class ApplicationService(ServiceObject):
    def __init__(self,name):
        self.name = name
        
        self._process = ProcessorService()
    
    def start(self):
        if super(ApplicationService,self).start():
            self._process.start()
            
            self._client = MongoClient(HOST_NAME,PORT_NUMBER,document_class=ObjectDict)
            self._database = self._client[DATABASE_INSTANCE]
            self.behaviors = self._database[BEHAVIOR_COLLECTION]
            
            return True
        else:
            return False
            
    def stop(self):
        if super(ApplicationService,self).stop():
            self._process.start()
            
            #self.behavior
            self._database.logout()
            self._client.disconnect()
            
            return True
        else:
            return False
            
    def pause(self):
        if super(ApplicationService,self).pause():
            self._process.pause()
            
            return True
        else:
            return False
            
    def resume(self):
        if super(ApplicationService,self).resume():
            self.run()
            
            self._process.resume()
            
            return True
        else:
            return False
            
    def run(self):
        if self._running:
            self._main = BehaviorFactory(self,self.name)(name=MAIN_NAME)
            self._process.schedule(self._main.control,self._main.name,Ellipsis)
        else:
            self.resume()