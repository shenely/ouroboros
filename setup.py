from setuptools import setup

setup(name="ouroboros",
      version="0.1",
      author="shenely",
      description="A serpent eating its own tail",
      packages=["ouroboros",
                "ouroboros.lib"],
      install_requires=["ob-core",
                        "ob-time",
                        "ob-math",
                        "ob-orbit",
                        "ob-web"])

