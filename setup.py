import os.path
from setuptools import setup

env = os.getenv('VIRTUAL_ENV', os.sep)
web = os.path.join(env, 'var', 'www', 'ouroboros')

setup(name='ouroboros',
      version='0.1',
      author='shenely',
      description='A serpent eating its own tail',
      package_dir={'ouroboros': 'ouroboros'},
      packages=['ouroboros',
                'ouroboros.ext'],
      install_requires=['tornado'])

