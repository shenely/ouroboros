import pkgutil
 
any((module_loader
     .find_module(name)
     .load_module(".".join([__name__, name])))
    for (module_loader, name, ispkg)
    in pkgutil.walk_packages(__path__)
    if ispkg is False)
