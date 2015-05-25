import pickle

from behavior import CompositeBehavior

transmitter = {
    "name": "Transmitter",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {
              "data":{
                      "require":[],
                      "provide":[
                                 {"name":"message","type":"StringPrimitive"}
                                 ]},
              "control":{"input":[],
                         "output":["success","failure"]}},
   "nodes": [
             {"name":"clock","type":"ContinuousClock","args":[]},
             {"name":"format","type":"MessageFormat","args":[]},
             {"name":"epoch","type":"DatetimePrimitive","args":[]},
             {"name":"message","type":"StringPrimitive","args":[]}
             ],
   "edges":{
            "data":[
                    {"source":{"node":"message","face":None},
                     "target":{"node":"Transmitter","face":"message"}},
                    {"source":{"node":"epoch","face":None},
                     "target":{"node":"clock","face":"epoch"}},
                    {"source":{"node":"clock","face":"message"},
                     "target":{"node":"format","face":"object"}},
                    {"source":{"node":"format","face":"message"},
                     "target":{"node":"message","face":None}}],
            "control":[{"source":{"node":"clock","face":"output"},
                        "target":{"node":"format","face":"input"}},
                       {"source":{"node":"format","face":"output"},
                        "target":{"node":"Transmitter","face":"success"}}]
            }
}

receiver = {
    "name": "Receiver",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "faces": {
              "data":{
                      "require":[
                                 {"name":"message","type":"StringPrimitive"}
                                 ],
                      "provide":[]},
              "control":{"input":["input"],
                         "output":["success","failure"]}},
   "nodes": [
             {"name":"parse","type":"MessageParse","args":[]},
             {"name":"epoch","type":"DatetimePrimitive","args":[]},
             {"name":"message","type":"StringPrimitive","args":[]}
             ],
   "edges":{
            "data":[
                    {"source":{"node":"Receiver","face":"message"},
                     "target":{"node":"message","face":None}},
                    {"source":{"node":"parse","face":"object"},
                     "target":{"node":"epoch","face":None}},
                    {"source":{"node":"message","face":None},
                     "target":{"node":"parse","face":"message"}}],
            "control":[{"source":{"node":"Receiver","face":"input"},
                        "target":{"node":"parse","face":"input"}},
                       {"source":{"node":"parse","face":"output"},
                        "target":{"node":"Receiver","face":"success"}}]
            }
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
   "nodes": [
             {"name":"receiver","type":"Receiver","args":[]},
             {"name":"transmitter","type":"Transmitter","args":[]}
             ],
   "edges":{
            "data":[
                    {"source":{"node":"transmitter","face":"message"},
                     "target":{"node":"receiver","face":"message"}}],
            "control":[{"source":{"node":"transmitter","face":"success"},
                        "target":{"node":"receiver","face":"input"}},
                       {"source":{"node":"receiver","face":"success"},
                        "target":{"node":"main","face":"success"}}]
            }
}