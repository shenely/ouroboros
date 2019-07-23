# built-in libraries
import os
import datetime

# external libraries
# ...

# internal libraries
# ...

# exports
__all__ = ("VIRTUAL_ENV",
           "PORT",
           "MILLI",
           "INFINITY",
           "ISO_8601", "UNIX_EPOCH",
           "CLOUD", "STONE")

# constants
VIRTUAL_ENV = os.getenv("VIRTUAL_ENV", os.sep)
PORT = os.getenv("OB_PORT", 8888)

MILLI = 1e-3

INFINITY = float("inf")

ISO_8601 = "%Y-%m-%dT%H:%M:%S.%fZ"
UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)

CLOUD = {}  # image catelog
STONE = {}  # type catelog
