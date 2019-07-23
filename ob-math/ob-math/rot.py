# built-in imports
# ...

# external imports
# ...

# internal imports
from ouroboros import Type
from ouroboros.lib import libquat

# exports
__all__= ("quat2rec", "rec2quat",
          "quat2rpy", "rpy2quat",
          "quat2mat", "mat2quat")

# constants
KILO = 1e3
MICRO = 1e-6

quat = Type(".rot#quat", "!rot/quat", libquat.quat,
            lambda x: [x.one, x.bar],
            lambda x: libquat.quat(*x))


def quat2rec():pass
def rec2quat():pass
def quat2rpy():pass
def rpy2quat():pass
def quat2mat():pass
def mat2quat():pass
