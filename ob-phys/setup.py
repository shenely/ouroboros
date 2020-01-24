import os
import time

from setuptools import setup

major = 0
minor = 1
micro = int(time.time())
__version__ = f"%d.%d.%d" % (major, minor, micro)

static = os.path.join("srv", "ouroboros")
js = os.path.join(static, "js")

setup(name="ob-phys",
      version=__version__,
      author="shenely",
      description="What sex is to masturbation",
      package_dir={"ouroboros.extra.phys": "ob-phys",
                   "ouroboros.lib": "lib",
                   "ouroboros.test": "test"},
      packages=["ouroboros.extra.phys",
                "ouroboros.lib"],
      data_files=[(js, ["static/js/ob-phys.js"])],
      install_requires=["ouroboros",
                        "ob-math",
                        "numpy",
                        "scipy"])

