#!/usr/bin/env python2.7

"""Comparison behaviors

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-09-11    shenely         1.0         Initial revision
2014-10-20    shenely         1.1         Incorporated a margin
2014-11-14    shenely         1.2         Converted to stated machine
2015-04-21    shenely         1.3         Support for factory rewrite
2015-05-27    shenely         1.4         Graph access by tuple
2015-06-04    shenely         1.5         Removed data graph outputs
2015-07-01    shenely         1.6         Removing unused dependencies
2016-06-18    shenely         1.7         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries

#Internal libraries
from ..behavior import behavior
from .watch import WatcherPrimitive
#
##################=


##################
# Export section #
#
__all__ = ["OrderComparison"]
#
##################


####################
# Constant section #
#
__version__ = "1.7"#current version [major.minor]
# 
####################


@behavior(name="OrderComparison",
          type="PrimitiveBehavior",
          faces={"data":{"require":[{"name":"reference",
                                     "type":"PrimitiveBehavior"},
                                    {"name":"margin",
                                     "type":"PrimitiveBehavior"},
                                    {"name":"object",
                                     "type":"PrimitiveBehavior"}],
                         "provide":[]},
                 "control":{"input":["input"],
                            "output":["after",
                                      "before",
                                      "around"]}},
          nodes=[{"name":"reference",
                  "type":"PrimitiveBehavior","args":[]},
                 {"name":"margin",
                  "type":"PrimitiveBehavior","args":[]},
                 {"name":"object",
                  "type":"PrimitiveBehavior","args":[]}],
          edges={"data":[{"source":{"node":"OrderComparison","face":"reference"},
                          "target":{"node":"reference","face":None}},
                         {"source":{"node":"OrderComparison","face":"margin"},
                          "target":{"node":"margin","face":None}},
                         {"source":{"node":"OrderComparison","face":"object"},
                          "target":{"node":"object","face":None}}],
                 "control":[]})
class OrderComparison(WatcherPrimitive):
    
    def _process(self):
        logging.debug("{0}:  Comparing".\
                      format(self.name))
            
        return self._compare()
        
    def _compare(self):
        reference = self._data_graph.node[("reference",)]["obj"]
        margin = self._data_graph.node[("margin",)]["obj"]
        object = self._data_graph.node[("object",)]["obj"]
        
        #XXX:  To account for the behavior factory metaclass
        assert issubclass(reference.__class__.__mro__[1],
                          object.__class__.__mro__[1]) \
            or issubclass(object.__class__.__mro__[1],
                          reference.__class__.__mro__[1])
        
        #NOTE:  Comparison values (shenely, 2014-10-20)
        # All relevant objects (object, reference, and margin) are
        #   expected to have a *.value that is a wrapped Python type
        #   (either built-in, from the standard library, or from a
        #   third-party library).  The value yielded by subtracting
        #   object from reference is assumed to be comparable to margin.
        if reference.value - object.value > margin.value:
            logging.info("{0}:  After".\
                     format(self.name))
            
            return "after"
        elif object.value - reference.value < margin.value:
            logging.info("{0}:  Before".\
                     format(self.name))
            
            return "before"
        else:
            logging.info("{0}:  Around".\
                     format(self.name))
            
            return "around"