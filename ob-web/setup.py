from setuptools import setup

setup(name="ob-web",
      version="0.1",
      author="shenely",
      description="A series of tubes",
      package_dir={"ouroboros.web": "ob-web"},
      packages=["ouroboros.web"],
      install_requires=["ob-core"])

