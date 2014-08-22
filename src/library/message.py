#!/usr/bin/env python2.7

"""Message behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 August 2014

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-08-22    shenely         1.0         Initial revision

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
from structure import *
from common import ObjectDict
from behavior import PrimitiveBehavior
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
__version__ = "1.0"#current version [major.minor]
# 
####################


@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class MessageParse(EventPrimitive):
    
    @required(PrimitiveBehavior)
    def template(self,value):pass
    
    @required(StringPrimitive)
    def message(self,value):pass
    
    @provided(PrimitiveBehavior)
    def object(self,value):pass
    
    def _occur(self):
        logging.info("{0}:  Parsing from {1}".\
                     format(self._name,self.message.value))
        
        self.object.value = self.template.object_hook(self.message.value)
        
        logging.info("{0}:  Parsed".\
                     format(self._name))

@behavior(who="me",
          when="now",
          where="here",
          what="that",
          why="because")
class MessageFormat(ActionPrimitive):
    
    @required(PrimitiveBehavior)
    def template(self,value):pass
    
    @required(PrimitiveBehavior)
    def object(self,value):pass
    
    @provided(StringPrimitive)
    def message(self,value):pass
    
    def _execute(self):
        logging.info("{0}:  Formatting".\
                     format(self.name))
        
        self.message.value = self.template.default(self.object.value)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self._name,self.message.value))