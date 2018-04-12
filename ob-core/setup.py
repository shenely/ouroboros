import os.path
from setuptools import setup

env = os.getenv('VIRTUAL_ENV', os.sep)
web = os.path.join(env, 'var', 'www', 'ouroboros')

setup(name='ob-core',
      version='0.1',
      author='shenely',
      description='In the middle of things',
      package_dir={'ouroboros': 'ob-core'},
      packages=['ouroboros'],
      install_requires=['tornado'])

