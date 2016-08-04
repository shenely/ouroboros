from setuptools import setup

setup(name="ob-core",
      version="0.1",
      author="shenely",
      description="In the middle of things",
      package_dir={"ouroboros": "ob-core"},
      packages=["ouroboros"],
      install_requires=["simpy>=3.0"])

