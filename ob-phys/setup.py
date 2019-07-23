from setuptools import setup

setup(name="ob-phys",
      version="0.1",
      author="shenely",
      description="What sex is to masturbation",
      package_dir={"ouroboros.ext.phys": "ob-phys",
                   "ouroboros.lib": "lib",
                   "ouroboros.test": "test"},
      packages=["ouroboros.ext.phys",
                "ouroboros.lib",
                "ouroboros.test"],
      install_requires=["ouroboros",
                        "ob-math",
                        "numpy",
                        "scipy"])

