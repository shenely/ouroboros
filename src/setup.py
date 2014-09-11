from service.persist import PersistenceService

service = PersistenceService()

service.start()
service.run()

import behavior as _

_.PrimitiveBehavior.install(service)
_.CompositeBehavior.install(service)

import library as _

_.NumberPrimitive.install(service)
_.StringPrimitive.install(service)
_.SourcePrimitive.install(service)
_.TargetPrimitive.install(service)
_.ConditionPrimitive.install(service)
_.EventPrimitive.install(service)
_.ActionPrimitive.install(service)

del _

import library.clock as _

_.DatetimePrimitive.install(service)
_.ElapsedPrimitive.install(service)
_.ContinuousClock.install(service)
_.DiscreteClock.install(service)

del _

import library.socket as _

_.SocketPrimitive.install(service)
_.SocketSubscribe.install(service)
_.SocketPublish.install(service)

del _

import library.message as _

_.MessageParse.install(service)
_.MessageFormat.install(service)

del _

import main as _
    
_.main.install(service)

del _

service.stop()