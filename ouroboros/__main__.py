import logging

import ouroboros
from ouroboros.service.execute import ExecutionService

ouroboros.install()

logging.basicConfig(level=logging.DEBUG)
    
app = ExecutionService("main")

app.start()
app.run()