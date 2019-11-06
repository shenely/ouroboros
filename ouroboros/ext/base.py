# built-in libraries
# ...

# external libraries
# ...

# internal libraries
from ouroboros import Image, Node

# exports
__all__ = ("nop", "eye")

# constants
# ...


@Image(".base@nop",
       param=Node(evs=(True,), args=(),
                  ins=(), reqs=(),
                  outs=(False,), pros=()))
def nop(param):
    """No-op"""
    yield
    while True:
        yield (param.outs((True,)),)


@Image(".base@eye",
       param=Node(evs=(True,), args=(),
                  ins=(), reqs=("arg",),
                  outs=(False,), pros=("ret",)))
def eye(param):
    """Identity function"""
    yield
    while True:
        value, = param.reqs
        param.pros = value,
        yield (param.outs((True,)),)
