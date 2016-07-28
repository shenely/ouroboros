import logging

from ouroboros_old.factory import BehaviorFactory

logging.basicConfig(level=logging.DEBUG)
    
main = BehaviorFactory("main")("main")
print main("input")
print main["epoch"]