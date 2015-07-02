from ouroboros.behavior import behavior
from ouroboros.lib import EventPrimitive
            
class OrbitEvent(EventPrimitive):pass
class PeriapsisEvent(OrbitEvent):pass
class ApoapsisEvent(OrbitEvent):pass
class AscendingNodeEvent(OrbitEvent):pass
class DescendingNodeEvent(OrbitEvent):pass
class NorthernPoleEvent(OrbitEvent):pass
class SouthernPoleEvent(OrbitEvent):pass