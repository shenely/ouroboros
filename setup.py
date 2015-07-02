from setuptools import setup

setup(name="ouroboros",
      version="0.1",
      author="shenely",
      description="A serpent eating its own tail",
      packages=["ouroboros",
                "ouroboros.dev",
                "ouroboros.srv",
                "ouroboros.lib",
                "ouroboros.ext",
                #"ouroboros.orbit",
                ],
      install_requires=["networkx>=0.99",
                        "pymongo>=3.0",
                        "pyzmq>=2.0.7"
                        ],
      )
