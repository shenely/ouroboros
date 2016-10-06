from setuptools import setup

setup(name="ob-math",
      version="0.1",
      author="shenely",
      description="On the shoulders of giants",
      package_dir={"ouroboros.lib": "ob-math"},
      py_modules=["ouroboros.lib.vec",
                  "ouroboros.lib.rot"],
      install_requires=["ob-core",
                        "numpy>=1.11",
                        "scipy>0.18"])

