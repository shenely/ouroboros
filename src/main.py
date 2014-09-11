from common import ObjectDict
from behavior import CompositeBehavior

class main(CompositeBehavior):
    _doc = ObjectDict(
      name="main",
      type=None,
      story={ },
      nodes=[
        {
          "name": "clock",
          "type": "ContinuousClock",
          "pins": [ ]
        },
        {
          "name": "format",
          "type": "MessageFormat",
          "pins": [ ]
        },
        {
          "name": "publish",
          "type": "SocketPublish",
          "pins": [ { "name": "address", "value": "Clock.Test" } ]
        },
        {
          "name": "epoch",
          "type": "DatetimePrimitive",
          "pins": [ ]
        },
        {
          "name": "socket",
          "type": "SocketPrimitive",
          "pins": [ { "name": "type", "value": "PUB" } ]
        }
      ],
      links=[
        { 
          "source": { "node": "epoch", "pin": None },
          "target": { "node": "clock", "pin": "epoch" }
        },
        { 
          "source": { "node": "epoch", "pin": None },
          "target": { "node": "format", "pin": "template" }
        },
        { 
          "source": { "node": "clock", "pin": "message" },
          "target": { "node": "format", "pin": "object" }
        },
        { 
          "source": { "node": "socket", "pin": None },
          "target": { "node": "publish", "pin": "socket" }
        },
        { 
          "source": { "node": "format", "pin": "message" },
          "target": { "node": "publish", "pin": "message" }
        },
      ],
      pins=[ ],
      rules=[
        {
          "source": "clock",
          "events": [ ],
          "conditions": [ ],
          "actions": [ "format" ],
          "target": "publish"
        }
      ]
    )