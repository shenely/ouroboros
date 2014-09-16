import logging

from service.execute import ExecutionService

logging.basicConfig(level=logging.INFO)
    
app = ExecutionService("main")

app.start()
app.run()

