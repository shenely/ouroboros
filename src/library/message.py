#!/usr/bin/env python2.7

"""Message behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 August 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-21    shenely         1.0         Initial revision
2014-08-22    shenely         1.1         Combined behavior and structure

"""


##################
# Import section #
#
#Built-in libraries
import types
import logging

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
__version__ = "1.1"#current version [major.minor]
# 
####################


@required("template",PrimitiveBehavior)
@required("message",StringPrimitive)
@provided("object",PrimitiveBehavior)
@behavior()
class MessageParse(EventPrimitive):
    
    def template(self,value):pass
    
    def message(self,value):pass
    
    def object(self,value):pass
    
    def _occur(self):
        logging.info("{0}:  Parsing from {1}".\
                     format(self._name,self.message.value))
        
        self.object.value = self.template.object_hook(self.message.value)
        
        logging.info("{0}:  Parsed".\
                     format(self._name))

@required("template",PrimitiveBehavior)
@required("object",PrimitiveBehavior)
@provided("message",StringPrimitive)
@behavior()
class MessageFormat(ActionPrimitive):
    
    def template(self,value):pass
    
    def object(self,value):pass
    
    def message(self,value):pass
    
    def _execute(self):
        logging.info("{0}:  Formatting".\
                     format(self.name))
        
        self.message.value = self.template.default(self.object.value)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self._name,self.message.value))