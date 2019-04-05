# built-in imports
# ...

# external imports
# ...

# internal imports
from ouroboros import ENCODE, DECODE
from ouroboros.lib import libquat

# exports
__all__= (
    'quat2rec', 'rec2quat',
    'quat2rpy', 'rpy2quat',
    'quat2mat', 'mat2quat'
)

# constants
KILO = 1e3
MICRO = 1e-6

ENCODE[libquat.quat] = ('@quat', lambda x:[x.one, x.bar])
DECODE['@quat'] = lambda x:libquat.quat(*x)


def quat2rec():pass
def rec2quat():pass
def quat2rpy():pass
def rpy2quat():pass
def quat2mat():pass
def mat2quat():pass
