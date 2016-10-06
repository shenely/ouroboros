import tornado.ioloop

from . import Ouroboros
from .util import *

"""
/ob-rest-api/

system/ -> SystemHandler
GET -> SystemHandler.get {data: [String, ...]}
{data: [Object, ...]}
GET ?name=<name> -> SystemHandler.get {data: Object}
POST {data: Object} -> SystemHandler.post
DELETE ?name=<name> -> SystemHandler.delete

process/ -> ProcessHandler
GET -> ProcessHandler.get {data: [String, ...]}
GET name=<name> -> ProcessHandler.get {data: Object}

stream -> WebSocketHandler
WS -> WebSocket.open
SEND -> WebSocket.on_message
RECV -> WebSocket.write_message
"""

def main():
    loop = tornado.ioloop.IOLoop.current()
    env = TornadoEnvironment(loop, strict=False)
    
    ob = Ouroboros(env, loop)
    
    app = tornado.web.Application([(r"/ob-rest-api/system",
                                    SystemHandler, {"ob": ob}),
                                   (r"/ob-rest-api/process",
                                    ProcessHandler, {"ob": ob}),
                                   (r"/ob-rest-api/stream",
                                    WebSocketHandler, {"ob": ob})])
    app.listen(8000)
    
    loop.start()

if __name__ == '__main__':
    main()