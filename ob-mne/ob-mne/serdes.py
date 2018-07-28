#built-in libraries
import itertools

#external libraries
#...

#internal libraries
from ouroboros import NORMAL, Item, PROCESS

#exports
__all__ = ('ser', 'des')

#constants
BYTE = 8#bits

@PROCESS('mne.ser', NORMAL,
         Item('head',
              evs=('raw',), args=(),
              ins=('raw',), reqs=('raw',),
              outs=('eng',), pros=()),
         Item('body',
              evs=('raw',), args=(),
              ins=('raw',), reqs=('raw',),
              outs=('eng',), pros=()),
         Item('foot',
              evs=('raw',), args=(),
              ins=('raw',), reqs=('raw',),
              outs=('eng',), pros=()),
         Item('usr',
              evs=(), args=(),
              ins=(), reqs=(),
              outs=(True,), pros=('p',)))
def ser(head, body, foot, usr):
    """Serialize"""
    body_id = [_id for _id, in body]
    
    right = yield
    while True:
        head = right['head']
        (head,), _ = head.next()
        
        body = (((), (True,))
                if _id == head['id']
                else (None, None)
                for _id in body_id)
        left = {'body': body}
        right = yield left
        body = right['body']
        p = (raw for (raw,), (ev,) in body if ev).next()

        head = (((), (True,)),)
        left = {'head': head}
        right = yield left
        head = right['head']
        (head,), (ev,) = head.next()
        if ev:pass
        p[:len(head)] = head

        foot = (((), (True,)),)
        left = {'foot': foot}
        right = yield left
        foot = right['foot']
        (foot,), (ev,) = foot.next()
        if ev:pass
        p += foot

        usr = (((p,), (True,)),)
        left = {'usr': usr}
        right = yield left

@PROCESS('mne.des', NORMAL,
         Item('head',
              evs=('eng',), args=(),
              ins=('eng',), reqs=('eng',),
              outs=('raw',), pros=('raw',)),
         Item('body',
              evs=('eng',), args=('id',),
              ins=('eng',), reqs=(),
              outs=('raw',), pros=('raw',)),
         Item('foot',
              evs=('eng',), args=(),
              ins=('eng',), reqs=(),
              outs=('raw',), pros=('raw',)),
         Item('usr',
              evs=(True,), args=(),
              ins=(), reqs=('p',),
              outs=(), pros=()))
def des(head, body, foot, usr):
    """Deserialize"""
    body_id = [_id for _id, in body]
    
    right = yield
    while True:
        usr = right['usr']

        (p,), _ = usr.next()
        
        head = (((p,), (True,)),)
        left = {'head': head}
        right = yield left
        head = right['head']
        (head,), (ev,) = head.next()
        if ev:pass
        
        body = (((p,), (True,))
                if _id == head['id']
                else (None, None)
                for _id in body_id)
        left = {'body': body}
        right = yield left
        body = right['body']
        if any(ev for _, (ev,) in body):pass

        foot = (((p,), (True,)),)
        left = {'foot': foot}
        right = yield left
        foot = right['foot']
        _, (ev,) = foot.next()
        if ev:pass

        usr = (((), (True,)),)
        left = {'usr': usr}
        right = yield left
