#!/usr/bin/env python2.7

"""Ordering behaviors

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
from behavior import *
from . import ConditionPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["BeforeOrder",
           "AfterOrder"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################

    
@required("reference",PrimitiveBehavior)
@provided("object",PrimitiveBehavior)
class BeforeOrder(ConditionPrimitive):
    
    def _satisfy(self):
        assert type(self.reference) == type(self.object)
        
        if self.object.value > self.reference.value:
            logging.info("{0}:  After".\
                     format(self._name))
            
            return True
        else:
            logging.info("{0}:  Not after".\
                     format(self._name))
            
            return False

@required("reference",PrimitiveBehavior)
@provided("object",PrimitiveBehavior)
class AfterOrder(ConditionPrimitive):
    
    def _satisfy(self):
        assert type(self.reference) == type(self.object)
        
        if self.object.value < self.reference.value:
            logging.info("{0}:  Before".\
                     format(self._name))
            
            return True
        else:
            logging.info("{0}:  Not before".\
                     format(self._name))
            
            return False