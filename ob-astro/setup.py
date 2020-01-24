import os
import time

from setuptools import setup, Extension

major = 0
minor = 1
micro = int(time.time())
__version__ = f"%d.%d.%d" % (major, minor, micro)

static = os.path.join("srv", "ouroboros")
js = os.path.join(static, "js")

libunikep = Extension("_libunikep",
                      include_dirs=["include"],
                      sources=["src/unikep.c"])
liborbele = Extension("_liborbele",
                      include_dirs=["include"],
                      sources=["src/orbele.c"])
libgeoid = Extension("_libgeoid",
                     include_dirs=["include"],
                     sources=["src/geoid.c"])

setup(name="ob-astro",
      version=__version__,
      author="shenely",
      description="Circles within circles",
      package_dir={"ouroboros.extra.astro": "ob-astro",
                   "ouroboros.lib": "lib",
                   "ouroboros.test": "test"},
      packages=["ouroboros.extra.astro",
                "ouroboros.lib",
                "ouroboros.test"],
      ext_package="ouroboros.lib",
      ext_modules=[libunikep,
                   liborbele,
                   libgeoid],
      data_files=[(js, ["static/js/ob-astro.js"])],
      install_requires=["ouroboros",
                        "ob-time",
                        "ob-math",
                        "numpy",
                        "scipy",
                        "sgp4"])

