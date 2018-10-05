from setuptools import setup

setup(name='ob-data',
      version='0.1',
      author='shenely',
      description='Garbage in, garbage out',
      package_dir={'ouroboros.ext.data': 'ob-data'},
      packages=['ouroboros.ext.data'],
      install_requires=['ouroboros'])

