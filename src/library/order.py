#!/usr/bin/env python2.7

"""Comparison behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   20 October 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-11    shenely         1.0         Initial revision
2014-10-20    shenely         1.1         Incorporated a margin

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
__all__ = ["BeforeComparison",
           "AfterComparison"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################

    
@required("reference",PrimitiveBehavior)
@required("margin",PrimitiveBehavior)
@required("object",PrimitiveBehavior)
class BeforeComparison(ConditionPrimitive):
    
    def _satisfy(self):
        assert type(self.reference) == type(self.object)
        
        #NOTE:  Comparison values (shenely, 2014-10-20)
        # All relevant objects (object, reference, and margin) are
        #   expected to have a *.value that is a wrapped Python type
        #   (either built-in, from the standard library, or from a
        #   third-party library).  The value yielded by subtracting
        #   object from reference is assumed to be comparable to margin.
        if self.reference.value - self.object.value > self.margin.value:
            logging.info("{0}:  After".\
                     format(self._name))
            
            return True
        else:
            logging.info("{0}:  Not after".\
                     format(self._name))
            
            return False

@required("reference",PrimitiveBehavior)
@required("margin",PrimitiveBehavior)
@required("object",PrimitiveBehavior)
class AfterComparison(ConditionPrimitive):
    
    def _satisfy(self):
        assert type(self.reference) == type(self.object)
        
        #NOTE:  Comparison values (shenely, 2014-10-20)
        # All relevant objects (object, reference, and margin) are
        #   expected to have a *.value that is a wrapped Python type
        #   (either built-in, from the standard library, or from a
        #   third-party library).  The value yielded by subtracting
        #   reference from object is assumed to be comparable to margin.
        if self.object.value - self.reference.value < self.margin.value:
            logging.info("{0}:  Before".\
                     format(self._name))
            
            return True
        else:
            logging.info("{0}:  Not before".\
                     format(self._name))
            
            return False