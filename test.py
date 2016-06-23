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
                        "target":{"node":"Clock","face":"output"},
                        "default":True}]}}
service.set({ "name": clock["name"] },clock)

transmitter = {
    "name": "Transmitter",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[{"name":"queue","type":"QueuePrimitive"}],
                      "provide":[{"name":"message","type":"StringPrimitive"}]},
              "control":{"input":["input"],
                         "output":["output"]}},
   "nodes": [{"name":"queue","type":"QueuePrimitive","args":[]},
             {"name":"priority","type":"NumberPrimitive",
              "args":[{"name":"value","value":0}]},
             {"name":"get","type":"QueueGet","args":[]},
             {"name":"format","type":"MessageFormat","args":[]},],
   "edges":{"data":[{"source":{"node":"queue","face":None},
                     "target":{"node":"get","face":"queue"}},
                    {"source":{"node":"get","face":"priority"},
                     "target":{"node":"priority","face":None}},
                    {"source":{"node":"get","face":"object"},
                     "target":{"node":"format","face":"object"}},
                    {"source":{"node":"Transmitter","face":"queue"},
                     "target":{"node":"queue","face":None}},
                    {"source":{"node":"format","face":"message"},
                     "target":{"node":"Transmitter","face":"message"}}],
            "control":[{"source":{"node":"Transmitter","face":"input"},
                        "target":{"node":"get","face":"input"}},
                       {"source":{"node":"get","face":"output"},
                        "target":{"node":"format","face":"input"}},
                       {"source":{"node":"format","face":"output"},
                        "target":{"node":"Transmitter","face":"output"}}]}}
service.set({ "name": transmitter["name"] },transmitter)

receiver = {
    "name": "Receiver",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[{"name":"message","type":"StringPrimitive"}],
                      "provide":[ ]},
              "control":{"input":["input"],
                         "output":["success","failure"]}},
   "nodes": [{"name":"parse","type":"MessageParse","args":[]},
             {"name":"epoch","type":"DatetimePrimitive","args":[]}],
   "edges":{"data":[{"source":{"node":"Receiver","face":"message"},
                     "target":{"node":"parse","face":"message"}},
                    {"source":{"node":"parse","face":"object"},
                     "target":{"node":"epoch","face":None}}],
            "control":[{"source":{"node":"Receiver","face":"input"},
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
                     "target":{"node":"transmitter","face":"queue"}},
                    {"source":{"node":"transmitter","face":"message"},
                     "target":{"node":"receiver","face":"message"}}],
            "control":[{"source":{"node":"clock","face":"output"},
                        "target":{"node":"transmitter","face":"input"}},
                       {"source":{"node":"transmitter","face":"output"},
                        "target":{"node":"receiver","face":"input"}},
                       {"source":{"node":"receiver","face":"success"},
                        "target":{"node":"main","face":"success"}}]}}
service.set({ "name": main["name"] },main)

service.pause()
service.stop()

import ouroboros.__main__

