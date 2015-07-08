#!/usr/bin/env python2.7

"""Math library

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   07 July 2015

TBD.

Classes:
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2015-07-07    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries
from numpy import ndarray,array
from numpy.polynomial import Polynomial

#Internal libraries
from ouroboros.behavior import behavior,PrimitiveBehavior
from ouroboros.lib.watch import WatcherPrimitive
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
__version__ = "1.0"#current version [major.minor]
# 
####################


@behavior(name="ArrayPrimitive",
          type="PrimitiveBehavior")
class ArrayPrimitive(PrimitiveBehavior):
    
    def _update(self,*args,**kwargs):
        self.value = kwargs.pop("value")
        
        if isinstance(self.value,types.DictType):
            self.value = self.object_hook(self.value)
        
        assert isinstance(self.value,ndarray)
        
        super(ArrayPrimitive,self)._update(*args,**kwargs)
        
    def default(self,obj):
        if isinstance(obj,ndarray):
            obj = { "$array": obj.tolist() }
        else:
            obj = super(ArrayPrimitive,self).default(obj)
            
        return obj
        
    def object_hook(self,dct):
        dct = super(ArrayPrimitive,self).object_hook(dct)
        
        if isinstance(dct,types.DictType):
            if "$array" in dct:
                values = dct["$array"]
                
                assert isinstance(values,types.ListType)
                
                dct = array(values)
    
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
class PolynomialPrimitive(PrimitiveBehavior,WatcherPrimitive):
    
    def _update(self,*args,**kwargs):
        domain = self._data_graph.node[("domain",)]["obj"]
        window = self._data_graph.node[("window",)]["obj"]
        coeff = self._data_graph.node[("window",)]["obj"]
        
        assert domain.value.shape == (2,)
        assert window.value.shape == (2,)
        
        self.value = Polynomial(coeff.value,domain.value,window.value)
        self.diff = self.value.deriv()
        self.int = self.value.integ()
        
        super(PolynomialPrimitive,self)._update(*args,**kwargs)

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
                         format(self.name,x.value))
        
        return face
        
def install(service):
    ArrayPrimitive.install(service)
    PolynomialPrimitive.install(service)