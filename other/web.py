import zmq
from zmq.devices import ThreadDevice
import zmq.eventloop.zmqstream

zmq.eventloop.ioloop.install()

import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class ZMQWebSocket(tornado.websocket.WebSocketHandler):    
    def open(self):
        context = zmq.Context.instance()
        socket = context.socket(self._type)
        
        self._socket = zmq.eventloop.zmqstream.ZMQStream(socket)
    
    def on_close(self):
        self._socket.close()

class Publisher(ZMQWebSocket):
    _type = zmq.PUB
    
    def on_message(self,message):
        messages = self._address,str(message)
        
        self._socket.send_multipart(messages)
    
    def open(self,path):
        super(self).open()
        
        self._address = ".".join(map(str.capitalize,path.split("/")))
        
        self._socket.connect("tcp://127.0.0.1:5555")

class Subscriber(ZMQWebSocket):
    _type = zmq.SUB
    
    def recv_multipart(self,messages):
        address,message = messages
        
        self.write_message(message)
    
    def open(self,path):
        super(self).open()
        
        self._address = ".".join(map(str.capitalize,path.split("/")))
        
        self._socket.connect("tcp://127.0.0.1:5556")
        self._socket.setsockopt(zmq.SUBSCRIBE,self._address)
        
        self._socket.on_recv(self.recv_multipart)

def main():
    proxy = ThreadDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
    proxy.bind_in("tcp://127.0.0.1:5555")
    proxy.bind_out("tcp://127.0.0.1:5556")
    proxy.setsockopt_in(zmq.SUBSCRIBE,"")

    # app = tornado.web.Application([(r"/", MainHandler),
    #                                (r"/pub/(.*)",Publisher),
    #                                (r"/sub/(.*)",Subscriber)],
    #                               template_path="./web/templates",
    #                               static_path="./web/static")
    # app.listen(8080)
    
if __name__ == '__main__':
    main()