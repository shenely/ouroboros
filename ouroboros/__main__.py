import logging

import ouroboros
from ouroboros.srv.execute import ExecutionService

ouroboros.install()

logging.basicConfig(level=logging.DEBUG)
    
app = ExecutionService("main")

app.start()
app.run()