import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop import ioloop

ioloop.install()

from tornado.web import StaticFileHandler,Application
from tornado.websocket import WebSocketHandler

class ZMQWebSocket(WebSocketHandler):
    def __init__(self,*args,**kwargs):
        self._socket = kwargs.pop("socket")

        super(ZMQWebSocket,self).__init__(*args,**kwargs)

    def open(self):
        self._stream = ZMQStream(self._socket)
        self._stream.on_recv(self.recv)

    def on_close(self):
        self._stream.close()

    def on_message(self,msg):
        self._stream.send(msg)

    def recv(self,msgs):
        msg = msgs[0]

        self.write_message(msg)

def main():
    context = zmq.Context.instance()

    data = context.socket(zmq.PAIR)
    data.bind("inproc://data")

    ctrl = context.socket(zmq.PAIR)
    ctrl.bind("inproc://ctrl")

    app = Application([(r"/data",ZMQWebSocket, {"socket": data}),
                       (r'/static/(.*)', StaticFileHandler, {"path": "static"})])
    app.listen(8080)

if __name__ == '__main__':
    main()