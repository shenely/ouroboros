import math
import logging

from ...behavior import behavior
from ...lib import ActionPrimitive
from ...lib.watch import WatcherPrimitive

@behavior(name="EphemerisPrimitive",
          type="ActionPrimitive")
class EphemerisPrimitive(ActionPrimitive, WatcherPrimitive):pass

@behavior(name="OrbitalEphemeris",
          type="PrimitiveBehavior")
class OrbitalEphemeris(EphemerisPrimitive):pass

@behavior(name="DevelopmentEphemeris",
          type="PrimitiveBehavior")
class DevelopmentEphemeris(EphemerisPrimitive):pass