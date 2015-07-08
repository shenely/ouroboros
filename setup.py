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
                #"ouroboros.ext.orbit",
                ],
      install_requires=["networkx>=0.99",
                        "pymongo>=3.0",
                        "pyzmq>=2.0.7"
                        ],
      )

setup(name="ob-math",
      version="0.1",
      author="shenely",
      description="On the shoulders of giants",
      packages=["ouroboros.ext.physics",],
      install_requires=["ouroboros",
                        "numpy>=1.4.0"],
      )

setup(name="ob-orbit",
      version="0.1",
      author="shenely",
      description="Circles within circles",
      packages=["ouroboros.ext.orbit",],
      install_requires=["ouroboros",
                        "ob-math",
                        "sgp4",
                        "jplephem",
                        "de405"],
      )

