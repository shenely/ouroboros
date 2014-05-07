#!/usr/bin/env python2.7

"""Service objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 May 2014

TBD.

Classes:
ServiceObject -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-05-05    shenely         1.0         Initial revision

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
__all__ = []
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ServiceObject(BaseObject):
    
    _started = False
    _running = False
                
    def start(self):
        if not self._started:
            self._started = True
            
            return True
        else:
            return False
        
    def stop(self):
        if self._started:
            self._started = False
            
            return True
        else:
            return False
            
    def pause(self):
        if self._started and self._running:
            self._running = False
            
            return True
        else:
            return False
                        
    def resume(self):
        if self._started and not self._running:
            self._running = True
            
            return True
        else:
            return False
        
    def run(self):
        raise NotImplemented