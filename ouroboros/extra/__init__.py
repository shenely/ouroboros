import importlib
import pkgutil

all(importlib.import_module(name)
    for (finder, name, ispkg)
    in pkgutil.walk_packages(__path__, __package__ + '.')
    if ispkg is False)
