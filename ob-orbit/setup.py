from setuptools import setup

setup(name="ob-orbit",
      version="0.1",
      author="shenely",
      description="Circles within circles",
      package_dir={"ouroboros.lib": "ob-orbit"},
      py_modules=["ouroboros.lib.geo",
                  "ouroboros.lib.orb"],
      install_requires=["ob-core"])

