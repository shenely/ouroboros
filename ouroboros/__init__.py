def install():
    from .service.persist import PersistenceService
    
    service = PersistenceService()
    
    service.start()
    service.run()
    
    from . import library as _
    _.install(service)
    
    #from . import ext as _
    #_.install(service)
        
    service.pause()
    service.stop()