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
def nop(arg):
    """No-op"""
    yield
    while True:
        yield (param.ctrl.send((True,)),)


@Image(".base@eye",
       param=Node(evs=(True,), args=(),
                ins=(), reqs=("arg",),
                outs=(False,), pros=("ret",)))
def eye(arg, ret):
    """Identity function"""
    yield
    while True:
        value, = next(param.data)
        param.data.send((value,))
        yield (param.ctrl.send((True,)),)
