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
          "name": "parse",
          "type": "MessageParse",
          "pins": [ ]
        },
        {
          "name": "publish",
          "type": "SocketPublish",
          "pins": [ { "name": "address", "value": "Clock.Test" } ]
        },
        {
          "name": "subscribe",
          "type": "SocketSubscribe",
          "pins": [ { "name": "address", "value": "Clock.Test" } ]
        },
        {
          "name": "epoch",
          "type": "DatetimePrimitive",
          "pins": [ ]
        },
        {
          "name": "receive",
          "type": "SocketPrimitive",
          "pins": [ { "name": "type", "value": "SUB" },
                    { "name": "address", "value": "tcp://127.0.0.1:5556" },
                    { "name": "identity", "value": "recv" } ]
        },
        {
          "name": "transmit",
          "type": "SocketPrimitive",
          "pins": [ { "name": "type", "value": "PUB" },
                    { "name": "address", "value": "tcp://127.0.0.1:5555" },
                    { "name": "identity", "value": "send" } ]
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
          "source": { "node": "epoch", "pin": None },
          "target": { "node": "parse", "pin": "template" }
        },
        { 
          "source": { "node": "clock", "pin": "message" },
          "target": { "node": "format", "pin": "object" }
        },
        { 
          "source": { "node": "format", "pin": "message" },
          "target": { "node": "publish", "pin": "message" }
        },
        { 
          "source": { "node": "subscribe", "pin": "message" },
          "target": { "node": "parse", "pin": "message" }
        },
        { 
          "source": { "node": "transmit", "pin": None },
          "target": { "node": "publish", "pin": "socket" }
        },
        { 
          "source": { "node": "receive", "pin": None },
          "target": { "node": "subscribe", "pin": "socket" }
        }
      ],
      pins=[ ],
      rules=[
        {
          "source": "clock",
          "events": [ ],
          "conditions": [ ],
          "actions": [ "format" ],
          "target": "publish"
        },
        {
          "source": "subscribe",
          "events": [ "parse" ],
          "conditions": [ ],
          "actions": [ ],
          "target": None
        }
      ]
    )