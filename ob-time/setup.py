from setuptools import setup

setup(name="ob-time",
      version="0.1",
      author="shenely",
      description="A brief history",
      package_dir={"ouroboros.lib": "ob-time"},
      py_modules=["ouroboros.lib.time"],
      install_requires=["ob-core"])

