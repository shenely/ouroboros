#!/usr/bin/env python2.7

"""Math library

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 June 2016

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision
2016-06-18    shenely         1.1         General code cleanup

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries
import numpy
import numpy.polynomial

#Internal libraries
from ...behavior import behavior, PrimitiveBehavior
from ...library.watch import WatcherPrimitive
#
##################


##################
# Export section #
#
__all__ = ["ArrayPrimitive",
           "PolynomialPrimitive"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
# 
####################


@behavior(name="ArrayPrimitive",
          type="PrimitiveBehavior")
class ArrayPrimitive(PrimitiveBehavior):
    
    def init(self,*args,**kwargs):
        self.value = kwargs.pop("value")
        
        if isinstance(self.value, types.DictType):
            self.value = self.object_hook(self.value)
        
        assert isinstance(self.value, numpy.ndarray)
        
        super(ArrayPrimitive, self).init(*args, **kwargs)
        
    def default(self,obj):
        if isinstance(obj, numpy.ndarray):
            obj = {"$array": obj.tolist()}
        else:
            obj = super(ArrayPrimitive, self).default(obj)
            
        return obj
        
    def object_hook(self,dct):
        dct = super(ArrayPrimitive, self).object_hook(dct)
        
        if isinstance(dct, types.DictType):
            if "$array" in dct:
                values = dct["$array"]
                
                assert isinstance(values, types.ListType)
                
                dct = numpy.array(values)
    
        return dct

@behavior(name="PolynomialPrimitive",
          type="PrimitiveBehavior",
          faces={"data":{"require":[{"name":"domain","type":"ArrayPrimitive"},
                                    {"name":"window","type":"ArrayPrimitive"},
                                    {"name":"coeff","type":"ArrayPrimitive"},
                                    {"name":"x","type":"NumberPrimitive"}],
                         "provide":[{"name":"y","type":"NumberPrimitive"}]},
                 "control":{"input":["up","diff","value","int"],
                            "output":["up","diff","value","int"]}},
          nodes=[{"name":"domain","type":"ArrayPrimitive","args":[]},
                 {"name":"window","type":"ArrayPrimitive","args":[]},
                 {"name":"coeff","type":"ArrayPrimitive","args":[]},
                 {"name":"x","type":"NumberPrimitive","args":[]},
                 {"name":"y","type":"NumberPrimitive","args":[]}],
          edges={"data":[{"source":{"node":"PolynomialPrimitive","face":"domain"},
                          "target":{"node":"domain","face":None}},
                         {"source":{"node":"PolynomialPrimitive","face":"window"},
                          "target":{"node":"window","face":None}},
                         {"source":{"node":"PolynomialPrimitive","face":"coeff"},
                          "target":{"node":"coeff","face":None}},
                         {"source":{"node":"PolynomialPrimitive","face":"x"},
                          "target":{"node":"x","face":None}},
                         {"source":{"node":"y","face":None},
                          "target":{"node":"PolynomialPrimitive","face":"y"}}],
                 "control":[]})
class PolynomialPrimitive(PrimitiveBehavior, WatcherPrimitive):
    
    def init(self, *args, **kwargs):
        domain = self._data_graph.node[("domain",)]["obj"]
        window = self._data_graph.node[("window",)]["obj"]
        coeff = self._data_graph.node[("window",)]["obj"]
        
        assert domain.value.shape == (2,)
        assert window.value.shape == (2,)
        
        self.value = numpy.polynomial.Polynomial(coeff.value,
                                                 domain.value,
                                                 window.value)
        self.diff = self.value.deriv()
        self.int = self.value.integ()
        
        super(PolynomialPrimitive, self).init(*args, **kwargs)

    def _process(self,face):
        if face == "up":
            logging.info("{0}:  Updating".\
                         format(self.name))
            
            domain = self._data_graph.node[("domain",)]["obj"]
            window = self._data_graph.node[("window",)]["obj"]
        
            assert domain.value.shape == (2,)
            assert window.value.shape == (2,)
            
            self.value = self.value.convert(domain=domain.value,
                                            window=window.value)
            self.diff = self.value.deriv()
            self.int = self.value.integ()
            
            logging.info("{0}:  Updated".\
                         format(self.name))
        else:
            logging.info("{0}:  Evaluating".\
                         format(self.name))
            
            x = self._data_graph.node[("x",)]["obj"]
            y = self._data_graph.node[("y",)]["obj"]
            
            y.value = self.value(x.value) if face == "value" else \
                      self.diff(x.value) if face == "diff" else \
                      self.int(x.value) if face == "int" else \
                      None
            
            logging.info("{0}:  Evaluated at {1}".\
                         format(self.name, x.value))
        
        return face
        
def install(service):
    ArrayPrimitive.install(service)
    PolynomialPrimitive.install(service)