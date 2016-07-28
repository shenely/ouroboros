#!/usr/bin/env python2.7

"""Database devices

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 June 2016

TBD.

Classes:
DatabaseDevice  -- TBD
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2014-06-26    shenely         1.0         Initial revision
2014-09-10    shenely         1.1         Saves don't modified document
2015-07-01    shenely         1.2         Added remove method
2016-06-22    shenely         1.3         Refactoring directories

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import pymongo

#Internal libraries
from ..common import ObjectDict
#
##################


##################
# Export section #
#
__all__ = ["DatabaseDevice"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]

#Default MongoDB settings
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 27017

DATABASE_INSTANCE = "ouroboros"
#
####################


class DatabaseDevice:
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._client = pymongo.MongoClient(host, port, document_class=ObjectDict)
        
    def __del__(self):
        self._client.close()
    
    def open(self, name=DATABASE_INSTANCE):
        self._database = self._client[name]
    
    def close(self):
        self._database.logout()
    
    def find(self, name, query):
        document = self._database[name].find_one(query)
        
        return document
    
    def save(self, name, query, document):
        _id = self._database[name].replace_one(query, document,
                                               upsert=True).upserted_id
        
        return _id
    
    def remove(self, name, query):
        self._database[name].delete_one(query)