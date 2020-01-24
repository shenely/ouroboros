import os
import time

from setuptools import setup

major = 0
minor = 1
micro = int(time.time())
__version__ = f"%d.%d.%d" % (major, minor, micro)

static = os.path.join("srv", "ouroboros")
js = os.path.join(static, "js")

setup(name="ob-math",
      version=__version__,
      author="shenely",
      description="On the shoulders of giants",
      package_dir={"ouroboros.extra.math": "ob-math",
                   "ouroboros.lib": "lib",
                   "ouroboros.test": "test"},
      packages=["ouroboros.extra.math",
                "ouroboros.lib"],
      data_files=[(js, ["static/js/ob-math.js"])],
      install_requires=["ouroboros",
                        "numpy",
                        "scipy"])

