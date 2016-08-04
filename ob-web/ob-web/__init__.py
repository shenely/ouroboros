import httplib

import tornado.web
import tornado.websocket

from ..util import coroutine, loads, dumps

__all__ = ["SystemHandler",
           "ProcessHandler",
           "WebSocketHandler"]

class BaseHandler(tornado.web.RequestHandler):
    
    def initialize(self, ob):
        self._ = ob

class SystemHandler(BaseHandler):
        
    def get(self):
        try:
            name = self.get_query_argument("name")
            data = self._.System[name]._config
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            data = sorted([name for name in self._.System])
            status = httplib.OK
        except IndexError:
            data = None
            status = httplib.NOT_FOUND
        except:
            data = None
            status = httplib.INTERNAL_SERVER_ERROR
        finally:
            self.add_header("Content-Type", "application/json")
            self.write(dumps({"data": data}))
            self.set_status(status)
        
    def post(self):
        try:
            data = loads(self.request.body)["data"]
            self._.start(data)
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        except IndexError:
            status = httplib.NOT_FOUND
        except:
            status = httplib.INTERNAL_SERVER_ERROR
            raise
        finally:
            self.set_status(status)
        
    def delete(self):
        try:
            self._.stop(self.get_query_argument("name"))
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            status = httplib.BAD_REQUEST
        except IndexError:
            status = httplib.NOT_FOUND
        except:
            status = httplib.INTERNAL_SERVER_ERROR
            raise
        finally:
            self.set_status(status)

class ProcessHandler(BaseHandler):
        
    def get(self):
        try:
            name = self.get_query_argument("name")
            data = [config._asdict() for config
                    in self._.Process[name]._config]
            status = httplib.OK
        except tornado.web.MissingArgumentError:
            data = sorted([name for name in self._.Process])
            status = httplib.OK
        except IndexError:
            data = None
            status = httplib.NOT_FOUND
        except:
            data = None
            status = httplib.INTERNAL_SERVER_ERROR
            raise
            
        self.add_header("Content-Type", "application/json")
        self.write(dumps({"data": data}))
        self.set_status(status)

class WebSocketHandler(tornado.websocket.WebSocketHandler, BaseHandler):
    
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self._packet = {}
        
        @coroutine
        def wrapper():
            while True:
                yield self._._env.timeout(1)
                if not self.close_code:
                    map(lambda packet:
                        self.write_message(dumps(packet)),
                        [{"name": name,
                          "data": [{"key": default(key),
                                    "value":self._packet[name]["data"][key]}
                                   for key in self._packet[name]["data"]],
                          "ctrl": list(self._packet[name]["ctrl"])}
                         for name in self._packet])
                self._packet.clear()
        self._._env.process(wrapper())
    
    def open(self):
        for name in self._.System:
            self._.System[name].watch(self._on_data)
            self._.System[name].listen(self._on_ctrl)

    def on_close(self):
        for name in self._.System:
            self._.System[name].unwatch(self._on_data)
            self._.System[name].unlisten(self._on_ctrl)

    def on_message(self, message):
        packet = loads(message)
        
        name = packet["name"]
        if "data" in packet:
            packet["data"] = {d["key"]: d["value"]
                              for d in packet["data"]}
            self._.System[name].set(packet["data"])
        if "ctrl" in packet:
            self._.System[name].go(packet["ctrl"])

    def _on_data(self, name, packet):
        self._packet[name] = self._packet.get(name, {})
        self._packet[name]["data"] = self._packet[name].get("data", {})
        self._packet[name]["data"].update(packet)

    def _on_ctrl(self, name, packet):
        self._packet[name] = self._packet.get(name, {})
        self._packet[name]["ctrl"] = self._packet[name].get("ctrl", set())
        self._packet[name]["ctrl"] |= set(packet)