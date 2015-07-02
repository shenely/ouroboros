import pickle

from ouroboros.behavior import CompositeBehavior
from ouroboros.srv.persist import PersistenceService

service = PersistenceService()

service.start()
service.run()

clock = {
    "name": "Clock",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[],
                      "provide":[{"name":"queue","type":"QueuePrimitive"}]},
              "control":{"input":[],
                         "output":["output"]}},
   "nodes": [{"name":"clock","type":"ContinuousClock","args":[]},
             {"name":"priority","type":"NumberPrimitive",
              "args":[{"name":"value","value":0}]},
             {"name":"put","type":"QueuePut","args":[]},
             {"name":"queue","type":"QueuePrimitive","args":[]}],
   "edges":{"data":[{"source":{"node":"clock","face":"message"},
                     "target":{"node":"put","face":"object"}},
                    {"source":{"node":"priority","face":None},
                     "target":{"node":"put","face":"priority"}},
                    {"source":{"node":"queue","face":None},
                     "target":{"node":"put","face":"queue"}},
                    {"source":{"node":"queue","face":None},
                     "target":{"node":"Clock","face":"queue"}}],
            "control":[{"source":{"node":"clock","face":"output"},
                        "target":{"node":"put","face":"input"}},
                       {"source":{"node":"put","face":"output"},
                        "target":{"node":"Clock","face":"output"}}]}}
service.set({ "name": clock["name"] },clock)

transmitter = {
    "name": "Transmitter",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[{"name":"queue","type":"QueuePrimitive"}],
                      "provide":[]},
              "control":{"input":["input"],
                         "output":["output"]}},
   "nodes": [{"name":"queue","type":"QueuePrimitive","args":[]},
             {"name":"priority","type":"NumberPrimitive",
              "args":[{"name":"value","value":0}]},
             {"name":"get","type":"QueueGet","args":[]},
             {"name":"format","type":"MessageFormat","args":[]},
             {"name":"publish","type":"SocketPublish",
              "args":[{ "name": "address", "value": "system.clock.epoch" }]},
             {"name":"socket","type":"SocketPrimitive",
              "args":[{ "name": "type", "value": "PUB" },
                      { "name": "address", "value": "tcp://localhost:5555" }]}],
   "edges":{"data":[{"source":{"node":"queue","face":None},
                     "target":{"node":"get","face":"queue"}},
                    {"source":{"node":"priority","face":None},
                     "target":{"node":"get","face":"priority"}},
                    {"source":{"node":"get","face":"object"},
                     "target":{"node":"format","face":"object"}},
                    {"source":{"node":"format","face":"message"},
                     "target":{"node":"publish","face":"message"}},
                    {"source":{"node":"socket","face":None},
                     "target":{"node":"publish","face":"socket"}},
                    {"source":{"node":"Transmitter","face":"queue"},
                     "target":{"node":"queue","face":None}}],
            "control":[{"source":{"node":"Transmitter","face":"input"},
                        "target":{"node":"get","face":"input"}},
                       {"source":{"node":"get","face":"output"},
                        "target":{"node":"format","face":"input"}},
                       {"source":{"node":"format","face":"output"},
                        "target":{"node":"publish","face":"input"}}]}}
service.set({ "name": transmitter["name"] },transmitter)

receiver = {
    "name": "Receiver",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[ ],
                      "provide":[ ]},
              "control":{"input":[],
                         "output":["success","failure"]}},
   "nodes": [{"name":"subscribe","type":"SocketSubscribe",
              "args":[{ "name": "address", "value": "system.clock.epoch" }]},
             {"name":"parse","type":"MessageParse","args":[]},
             {"name":"epoch","type":"DatetimePrimitive","args":[]},
             {"name":"socket","type":"SocketPrimitive",
              "args":[{ "name": "type", "value": "SUB" },
                      { "name": "address", "value": "tcp://localhost:5556" }]}],
   "edges":{"data":[{"source":{"node":"socket","face":None},
                     "target":{"node":"subscribe","face":"socket"}},
                    {"source":{"node":"subscribe","face":"message"},
                     "target":{"node":"parse","face":"message"}},
                    {"source":{"node":"parse","face":"object"},
                     "target":{"node":"epoch","face":None}}],
            "control":[{"source":{"node":"subscribe","face":"output"},
                        "target":{"node":"parse","face":"input"}},
                       {"source":{"node":"parse","face":"output"},
                        "target":{"node":"Receiver","face":"success"}}]}}
service.set({ "name": receiver["name"] },receiver)

main = {
    "name": "main",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[],
                      "provide":[]},
              "control":{"input":[],
                         "output":["success","failure"]}},
   "nodes": [{"name":"clock","type":"Clock","args":[]},
             {"name":"transmitter","type":"Transmitter","args":[]},
             {"name":"receiver","type":"Receiver","args":[]}],
   "edges":{"data":[{"source":{"node":"clock","face":"queue"},
                     "target":{"node":"transmitter","face":"queue"}}],
            "control":[{"source":{"node":"clock","face":"output"},
                        "target":{"node":"transmitter","face":"input"}},
                       {"source":{"node":"receiver","face":"success"},
                        "target":{"node":"main","face":"success"}}]}}
service.set({ "name": main["name"] },main)

service.pause()
service.stop()

import ouroboros.__main__

