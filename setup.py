from setuptools import setup

setup(name="ouroboros",
      version="0.1",
      author="shenely",
      description="A serpent eating its own tail",
      packages=["ouroboros"],
      install_requires=["simpy>=3.0",
                        "tornado>=4.2",
                        "numpy>=1.4",
                        "scipy>=0.15",
                        "sgp4"])

