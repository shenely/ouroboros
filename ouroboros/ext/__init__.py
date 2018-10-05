import pkgutil

all(module_loader
    .find_module(name)
    .load_module(name)
    for (module_loader, name, ispkg)
    in pkgutil.walk_packages(__path__, __package__ + '.')
    if ispkg is False)
