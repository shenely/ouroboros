#!/usr/bin/env python2.7

"""Service objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   07 June 2014

TBD.

Classes:
ServiceObject -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-05    shenely         1.0         Initial revision
2014-06-07    shenely                     Added documentation

"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
from common import BaseObject
#
##################=


##################
# Export section #
#
__all__ = ["ServiceObject"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ServiceObject(BaseObject):
    """Base service object"""
    
    _started = False#is the service started?
    _running = False#is the service running?
                
    def start(self):
        """Start the service."""
        if not self._started:
            self._started = True
            
            return True
        else:
            return False
        
    def stop(self):
        """Stop the service."""
        if self._started:
            self._started = False
            
            return True
        else:
            return False
            
    def pause(self):
        """Pause the service."""
        if self._started and self._running:
            self._running = False
            
            return True
        else:
            return False
                        
    def resume(self):
        """Resume the service."""
        if self._started and not self._running:
            self._running = True
            
            return True
        else:
            return False
        
    def run(self):
        raise NotImplemented# must override