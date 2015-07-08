def install():
    from ouroboros.srv.persist import PersistenceService
    
    service = PersistenceService()
    
    service.start()
    service.run()
    
    from . import lib as _
    _.install(service)
    
    #from . import ext as _
    #_.install(service)
        
    service.pause()
    service.stop()