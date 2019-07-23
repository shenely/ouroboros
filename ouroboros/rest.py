# built-in libraries
import os
import time
import json
import asyncio
import logging

# external libraries
import tornado.web
import tornado.websocket

# internal libraries
from ouroboros.conf import VIRTUAL_ENV, PORT
from ouroboros.util import default, object_hook

# exports
__all__ = ("FlagHandler",
           "InfoHandler",
           "DataHandler",
           "CtrlHandler",
           "StreamHandler",
           "init")

# constants
# ...

# logging
logger = logging.getLogger(__name__)


class ObRequestHandler(tornado.web.RequestHandler):

    def initialize(self, lake):
        self.lake = lake


class FlagHandler(ObRequestHandler):

    async def post(self):
        d = self.lake[None][True, None].data
        if d["f"].done():  # pause
            logger.debug("POST flag pause")
            d["f"] = asyncio.Future()
        else:  # resume
            logger.debug("POST flag resume")
            d["t"] = time.time()  # real time
            d["f"].set_result(True)


class InfoHandler(ObRequestHandler):

    async def get(self):
        logger.debug("GET info")
        d = self.lake[None][True, None].data
        obj = {"e": len(d["e"]),
               "q": len(d["q"]),
               "z": len(d["z"]),
               "f": d["f"].done()}
        s = json.dumps(obj)
        self.write(s)


class DataHandler(ObRequestHandler):

    async def get(self, _id, name):
        if _id.isdigit():
            _id = int(_id)
        if name.isdigit():
            name = int(name)
        logger.debug("GET data (%s.%s)", _id, name)
        item = self.lake[_id][False, name]
        obj = [{"key": key,
                "value": value}
               for (key, value)
               in item.data.items()]
        s = json.dumps(obj, default=default)
        self.write(s)

    async def put(self, _id, name):
        if _id.isdigit():
            _id = int(_id)
        if name.isdigit():
            name = int(name)
        logger.debug("PUT data (%s,%s)", _id, name)
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
        item = self.lake[_id][False, name]
        item["data"].update({pair["key"]: pair["value"]
                             for pair in obj
                             if pair["key"] in item.data})


class CtrlHandler(ObRequestHandler):

    async def post(self, _id, name):
        if _id.isdigit():
            _id = int(_id)
        if name.isdigit():
            name = int(name)
        logger.debug("POST ctrl (%s,%s)", _id, name)
        s = self.request.body
        obj = json.loads(s, object_hook=object_hook)
        e = self.lake[None][True, None].data["e"]
        item = self.lake[_id][False, name]
        any(e.add(item.data[pair["key"]])
            for pair in obj
            if pair["value"] is True
            and pair["key"] in item.ctrl)


class StreamHandler(tornado.websocket.WebSocketHandler,
                    ObRequestHandler):

    async def on_pong(self, data):
        d = self.lake[None][True, None].data
        if d["f"].done():
            e = d["e"]
            obj = [{"name": _id,
                    "items": [{"key": name[1],
                               "data": [{"key": key, "value": value}
                                        for (key, value)
                                        in item.data.items()],
                               "ctrl": [{"key": key, "value": ev in e}
                                        for (key, ev)
                                        in item.ctrl.items()]}
                              for (name, item) in model.items()
                              if name[0] is False]}
                   for (_id, model) in self.lake.items()
                   if _id is not None]
            s = json.dumps(obj, default=default)
            self.write_message(s)


def init(lake):
    web = os.path.join(VIRTUAL_ENV, "var", "www", "ouroboros")

    app = tornado.web.Application([
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": web}),
        (r"/ob-rest-api/flag", FlagHandler, {"lake": lake}),
        (r"/ob-rest-api/info", InfoHandler, {"lake": lake}),
        (r"/ob-rest-api/data/(\w+)/(\w+)", DataHandler, {"lake": lake}),
        (r"/ob-rest-api/ctrl/(\w+)/(\w+)", CtrlHandler, {"lake": lake}),
        (r"/ob-io-stream/", StreamHandler, {"lake": lake})
        ], websocket_ping_interval=1)
    app.listen(PORT)
