#built-in libraries
#...

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('parse', 'format')

#constants
BYTE = 8#bits

@PROCESS('mne.struct.parse', NORMAL,
         Item('mne',
              evs=('eng',), args=('byte', 'bit', 'size'),
              ins=('eng',), reqs=(),
              outs=('raw',), pros=('raw',)),
         Item('usr',
              evs=('raw',), args=(),
              ins=(), reqs=('raw',),
              outs=('eng',), pros=()))
def parse(mne, usr):
    """Struct parser"""
    spec = [(byte, byte + (bit + size) // BYTE + ((bit + size) % BYTE > 0),
             bit, BYTE - (bit + size) % BYTE)
            for (byte, bit, size) in mne]
    
    right = yield
    while True:
        usr = right['usr']
        (raw,), _ = usr.next()
        mne = (((reduce(lambda x, y:
                        (x << BYTE) | y, raw[start+1:end],
                        ((raw[start] << left) & 0xff) >> left) >> right,),
                (True,))
               for (start, end, left, right) in spec)
        left = {'mne': mne}
        right = yield left
        mne = right['mne']
        while all(ev for _, (ev,) in mne):
            right = yield {}
            mne = right['mne']
        
        usr = (((), (True,)),)
        left = {'usr': usr}
        right = yield left

@PROCESS('mne.struct.format', NORMAL,
         Item('mne',
              evs=('raw',), args=('byte', 'bit', 'size'),
              ins=('raw',), reqs=('raw',),
              outs=('eng',), pros=()),
         Item('usr',
              evs=('eng',), args=('size',),
              ins=(), reqs=(),
              outs=('raw',), pros=('raw',)))
def format(mne, usr):
    """Struct formatter"""
    spec = [(byte, byte + (bit + size) // BYTE + ((bit + size) % BYTE > 0),
             bit, BYTE - (bit + size) % BYTE)
            for (byte, bit, size) in mne]
    size, = usr.next()
    
    yield
    while True:
        mne = (((), (True,)) for _ in spec)
        left = {'mne': mne}
        right = yield left
        mne = right['mne']

        raw = [0] * (size // BYTE)#bytearray([0] * size)
        while True:
            for (start, end, left, right) in spec:
                (blah,), (ev,) = mne.next()
                if not ev:break
                
                raw[end-1] |= blah & ((0b1 << right) - 1)
                blah >>= right
                for i in xrange(end-2, start+1, -1):
                    raw[i] |= blah & 0xff
                    blah >>= BYTE
                raw[start] |= (blah & ((0b1 << left) - 1)) << (BYTE - left)
                blah >>= left
            else:break
            
            right = yield {}
            mne = right['mne']
            
        usr = (((raw,), (True,)),)
        left = {'usr': usr}
        yield left
