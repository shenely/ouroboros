from behavior import behavior,PrimitiveBehavior

class CelestialPrimitive(PrimitiveBehavior):pass
class StarPrimitive(CelestialPrimitive):pass
class Sun(StarPrimitive):pass
class PlanetPrimitive(CelestialPrimitive):pass
class Earth(PlanetPrimitive):pass
class EarthOld(Earth):pass
class EarthWGS72(Earth):pass
class EarthWGS84(Earth):pass
class MoonPrimitive(CelestialPrimitive):pass
class Moon(MoonPrimitive):pass