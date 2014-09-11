#!/usr/bin/env python2.7

"""Message behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 September 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision
2014-08-22    shenely         1.1         Combined behavior and structure
2014-09-10    shenely         1.2         Using JSON the right way

"""


##################
# Import section #
#
#Built-in libraries
import logging
import json

#External libraries
import zmq

#Internal libraries
from behavior import *
from . import StringPrimitive,EventPrimitive,ActionPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["MessageParse",
           "MessageFormat"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
# 
####################


@required("template",PrimitiveBehavior)
@required("message",StringPrimitive)
@provided("object",PrimitiveBehavior)
@behavior()
class MessageParse(EventPrimitive):
    
    def _occur(self):
        logging.info("{0}:  Parsing from {1}".\
                     format(self._name,self.message.value))
        
        self.object.value = json.loads(self.message.value,
                                       object_hook=self.template.object_hook)
        
        logging.info("{0}:  Parsed".\
                     format(self._name))

@required("template",PrimitiveBehavior)
@required("object",PrimitiveBehavior)
@provided("message",StringPrimitive)
@behavior()
class MessageFormat(ActionPrimitive):
    
    def _execute(self):
        logging.info("{0}:  Formatting".\
                     format(self._name))
        
        self.message.value = json.dumps(self.object.value,
                                        default=self.template.default)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self._name,self.message.value))