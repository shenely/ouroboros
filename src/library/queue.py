#!/usr/bin/env python2.7

"""Queue behaviors

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
from Queue import PriorityQueue
import logging

#External libraries

#Internal libraries
from behavior import *
from . import EventPrimitive,ActionPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["QueuePrimitive",
           "QueueGet",
           "QueuePut"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
# 
####################


class QueuePrimitive(PrimitiveBehavior):
    
    def __init__(self,name,pins,*args,**kwargs):            
        super(QueuePrimitive,self).__init__(name,pins,*args,**kwargs)
        
        self.value = PriorityQueue()
    
@required("queue",QueuePrimitive)
@required("priority",PrimitiveBehavior)
@provided("object",PrimitiveBehavior)
class QueueGet(EventPrimitive):
    
    def _occur(self):
        if not self.queue.value.empty(): 
            self.priority.value,self.object.value = self.queue.value.get()
                    
            logging.info("{0}: Got from queue".\
                         format(self._name))
            
            return Ellipsis
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self._name))

@required("queue",QueuePrimitive)
@required("priority",PrimitiveBehavior)
@required("object",PrimitiveBehavior)
class QueuePut(ActionPrimitive):
           
    def _execute(self):  
        if not self.queue.value.full():
            self.queue.value.put((self.priority.value,
                                  self.object.value))
                    
            logging.info("{0}:  Put to queue".\
                         format(self._name))
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))