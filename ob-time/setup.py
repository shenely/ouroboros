import os
import time

from setuptools import setup

major = 0
minor = 1
micro = int(time.time())
__version__ = f"%d.%d.%d" % (major, minor, micro)

static = os.path.join("srv", "ouroboros")
js = os.path.join(static, "js")

setup(name="ob-time",
      version=__version__,
      author="shenely",
      description="A brief history",
      package_dir={"ouroboros.extra.time": "ob-time"},
      packages=["ouroboros.extra.time"],
      data_files=[(js, ["static/js/ob-time.js"])],
      install_requires=["ouroboros",
                        "pytz"])

