#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
#...

@PROCESS('data.table.parse', NORMAL,
         Item('head',
              evs=('raw',), args=('size',),
              ins=('raw',), reqs=(),
              outs=('eng',), pros=('eng',)),
         Item('body',
              evs=('raw',), args=('size',),
              ins=('raw',), reqs=(),
              outs=('eng',), pros=('eng',)),
         Item('foot',
              evs=('raw',), args=('size',),
              ins=('raw',), reqs=(),
              outs=('eng',), pros=('eng',)),
         Item('usr',
              evs=('raw',), args=('count',),
              ins=(), reqs=('raw',),
              outs=('eng',), pros=('eng',)))
def parse(head, body, foot, usr):
    """Table parser"""
    hsize, = head.next()
    bsize, = body.next()
    fsize, = foot.next()
    count, = usr.next()
    
    right = yield
    while True:
        usr = right['usr']
        (raw,), _ = raw.next()
        
        eng = (((value,), (True,)),)

        left = {'eng': eng}
        right = yield left
