from math import sqrt,cos,sin
import logging

from ouroboros.behavior import behavior
from ouroboros.lib import ActionPrimitive
from ouroboros.lib.watch import WatcherPrimitive

@behavior(name="EphemerisPrimitive",
          type="ActionPrimitive")
class EphemerisPrimitive(ActionPrimitive,WatcherPrimitive):pass

@behavior(name="OrbitalEphemeris",
          type="PrimitiveBehavior")
class OrbitalEphemeris(EphemerisPrimitive):pass

@behavior(name="DevelopmentEphemeris",
          type="PrimitiveBehavior")
class DevelopmentEphemeris(EphemerisPrimitive):pass