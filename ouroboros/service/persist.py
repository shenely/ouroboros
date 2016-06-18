#!/usr/bin/env python2.7

"""Persistence service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   01 July 2015

TBD.

Classes:
PersistenceService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-06-12    shenely         1.0         Initial revision
2014-06-26    shenely         1.1         Moved database to device
2014-09-10    shenely         1.2         Added a run method
2015-07-01    shenely         1.3         Added delete method

"""


##################
# Import section #
#
#Built-in libraries
import types

#External libraries

#Internal libraries
from ..device.database import DatabaseDevice
from . import ServiceObject
#
##################


##################
# Export section #
#
__all__ = ["PersistenceService"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]

BEHAVIOR_COLLECTION = "behaviors"
#
####################


class PersistenceService(ServiceObject):                
    def start(self):
        if super(PersistenceService,self).start():
            self._database = DatabaseDevice()
            
            return True
        else:
            return False
        
    def stop(self):
        if super(PersistenceService,self).stop():
            del self._database
            
            return True
        else:
            return False
            
    def pause(self):
        if super(PersistenceService,self).pause():
            #XXX:  I don't know what to do here. (shenely, 2014-06-16)
            self._database.close()
            
            return True
        else:
            return False
                        
    def resume(self):
        if super(PersistenceService,self).resume():
            self._database.open()
            
            self.run()
            
            return True
        else:
            return False
            
    def run(self):
        self.resume() if not self._running else None
            
    def get(self,query):
        if self._running:
            document = self._database.find(BEHAVIOR_COLLECTION,query)# from database
            
            return document
        else:
            #TODO:  Persistence running exception (shenely, 2014-06-12)
            raise Exception# is not running
            
    def set(self,query,document):
        if self._running:
            self._database.save(BEHAVIOR_COLLECTION,query,document)# to database
        else:
            #TODO:  Persistence running exception (shenely, 2014-06-12)
            raise Exception# is not running
            
    def delete(self,query):
        if self._running:
            self._database.remove(BEHAVIOR_COLLECTION,query)# to database
        else:
            #TODO:  Persistence running exception (shenely, 2014-06-12)
            raise Exception# is not running