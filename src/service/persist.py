#!/usr/bin/env python2.7

"""Persistence service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 June 2014

TBD.

Classes:
PersistenceService -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-06-12    shenely         1.0         Initial revision
2014-06-26    shenely         1.1         Moved database to device

"""


##################
# Import section #
#
#Built-in libraries
import types

#External libraries

#Internal libraries
from . import ServiceObject
from device.database import DatabaseDevice
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
__version__ = "1.1"#current version [major.minor]

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
            
    def get(self,query):
        if self._running:
            document = self._database.find(BEHAVIOR_COLLECTION,query)# from database
            
            return document
        else:
            #TODO:  Persistence running exception (shenely, 2014-06-12)
            raise Exception# is not running
            
    def set(self,document):
        if self._running:
            self._database.save(BEHAVIOR_COLLECTION,document)# to database
        else:
            #TODO:  Persistence running exception (shenely, 2014-06-12)
            raise Exception# is not running