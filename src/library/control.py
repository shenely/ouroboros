#!/usr/bin/env python2.7

"""Control behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 September 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-11    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries

#Internal libraries
from . import ActionPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["ControlPrimitive",
           "AcceptedControl",
           "RejectedControl",
           "PositiveControl",
           "NegativeControl"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################


class ControlPrimitive(ActionPrimitive):
    
    def _process(self):
        logging.debug("{0}:  Executing".\
                      format(self._name))
        
        mode = self._execute()
        
        logging.debug("{0}:  Executed".\
                     format(self._name))
            
        return mode
    
class AcceptedControl(ControlPrimitive):
    
    def _execute(self):
        return Ellipsis
    
class RejectedControl(ControlPrimitive):
    
    def _execute(self):
        return None
    
class PositiveControl(ControlPrimitive):
    
    def _execute(self):
        return True
    
class NegativeControl(ControlPrimitive):
    
    def _execute(self):
        return False