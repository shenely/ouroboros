import pickle

from behavior import CompositeBehavior

transmitter = {
    "name": "Transmitter",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{"require":[],
                      "provide":[]},
              "control":{"input":[],
                         "output":[]}},
   "nodes": [{"name":"clock","type":"ContinuousClock","args":[]},
             {"name":"format","type":"MessageFormat","args":[]},
             {"name":"publish","type":"SocketPublish",
              "args":[{ "name": "address", "value": "system.clock.epoch" }]},
             {"name":"epoch","type":"DatetimePrimitive","args":[]},
             {"name":"socket","type":"SocketPrimitive",
              "args":[{ "name": "type", "value": "PUB" },
                      { "name": "address", "value": "tcp://localhost:5555" }]}],
   "edges":{"data":[{"source":{"node":"epoch","face":None},
                     "target":{"node":"clock","face":"epoch"}},
                    {"source":{"node":"clock","face":"message"},
                     "target":{"node":"format","face":"object"}},
                    {"source":{"node":"format","face":"message"},
                     "target":{"node":"publish","face":"message"}},
                    {"source":{"node":"socket","face":None},
                     "target":{"node":"publish","face":"socket"}}],
            "control":[{"source":{"node":"clock","face":"output"},
                        "target":{"node":"format","face":"input"}},
                       {"source":{"node":"format","face":"output"},
                        "target":{"node":"publish","face":"input"}}]}
}

receiver = {
    "name": "Receiver",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {"data":{
                      "require":[ ],
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
                        "target":{"node":"Receiver","face":"success"}}]}
}

main = {
    "name": "main",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {
              "data":{
                      "require":[],
                      "provide":[]},
              "control":{"input":[],
                         "output":["success","failure"]}},
   "nodes": [{"name":"receiver","type":"Receiver","args":[]},
             {"name":"transmitter","type":"Transmitter","args":[]}],
   "edges":{
            "data":[ ],
            "control":[{"source":{"node":"receiver","face":"success"},
                        "target":{"node":"main","face":"success"}}]
            }
}