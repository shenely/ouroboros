import os
import time

from setuptools import setup

major = 0
minor = 1
micro = int(time.time())
__version__ = f"%d.%d.%d" % (major, minor, micro)

static = os.path.join("srv", "ouroboros")
lib = os.path.join(static, "lib")
js = os.path.join(static, "js")
css = os.path.join(static, "css")

setup(name="ouroboros",
      version=__version__,
      author="shenely",
      description="A serpent eating its own tail",
      package_dir={"ouroboros": "ouroboros"},
      packages=["ouroboros",
                "ouroboros.extra"],
      data_files=[(static, ["static/index.html"]),
                  (lib, ["static/lib/vue.js"]),
                  (js, ["static/js/app.js",
                        "static/js/ouroboros.js",
                        "static/js/ob-model.js",
                        "static/js/ob-item.js",
                        "static/js/ob-datum.js"]),
                  (css, ["static/css/app.css"])],
      install_requires=["pyyaml",
                        "tornado"])

