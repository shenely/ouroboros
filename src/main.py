import pickle

from behavior import CompositeBehavior

transmitter = {
    "name": "Transmitter",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "nodes": [
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
            "name": "epoch",
            "type": "DatetimePrimitive",
            "pins": [ ]
        },
        {
            "name": "message",
            "type": "StringPrimitive",
            "pins": [ ]
        }
    ],
    "links": [
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
            "source": { "node": "format", "pin": "message" },
            "target": { "node": "message", "pin": None }
        }
    ],
    "pins": [ { "node": "message", "type": "provided" } ],
    "rules": [
        {
            "source": "clock",
            "events": [ ],
            "conditions": [ ],
            "actions": [ "format" ],
            "target": "Transmitter"
        }
    ]
}

receiver = {
    "name": "Receiver",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "nodes": [
        {
            "name": "parse",
            "type": "MessageParse",
            "pins": [ ]
        },
        {
            "name": "epoch",
            "type": "DatetimePrimitive",
            "pins": [ ]
        },
        {
            "name": "message",
            "type": "StringPrimitive",
            "pins": [ ]
        }
    ],
    "links": [
        { 
            "source": { "node": "epoch", "pin": None },
            "target": { "node": "parse", "pin": "template" }
        },
        { 
            "source": { "node": "parse", "pin": "object" },
            "target": { "node": "epoch", "pin": None }
        },
        { 
            "source": { "node": "message", "pin": None },
            "target": { "node": "parse", "pin": "message" }
        }
    ],
    "pins": [ { "node": "message", "type": "required" } ],
    "rules": [
        {
            "source": "Receiver",
            "events": [ "parse" ],
            "conditions": [ ],
            "actions": [ ],
            "target": None
        }
    ]
}

main = {
    "name": "main",
    "type": CompositeBehavior.__name__,
    "path": pickle.dumps(CompositeBehavior),
    "story": { },
    "nodes": [
        {
            "name": "receiver",
            "type": "Receiver",
            "pins": [ ]
        },
        {
            "name": "transmitter",
            "type": "Transmitter",
            "pins": [ ]
        }
    ],
    "links": [
        { 
            "source": { "node": "transmitter", "pin": "message" },
            "target": { "node": "receiver", "pin": "message" }
        }
    ],
    "pins": [ ],
    "rules": [
        {
            "source": "transmitter",
            "events": [ ],
            "conditions": [ ],
            "actions": [ ],
            "target": "receiver"
        }
    ]
}