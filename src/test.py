import logging

from service.execute import ExecutionService

logging.basicConfig(level=logging.DEBUG)
    
app = ExecutionService("main")

app.start()
app.run()

