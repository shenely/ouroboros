from setuptools import setup

setup(name="ouroboros",
      version="0.1",
      author="shenely",
      description="A serpent eating its own tail",
      package_dir={"ouroboros": "ouroboros"},
      packages=["ouroboros",
                "ouroboros.ext"],
      install_requires=["pyyaml",
                        "tornado"])

