import os.path
from setuptools import setup

env = os.getenv('VIRTUAL_ENV', os.sep)
web = os.path.join(env, 'var', 'www', 'ouroboros')

setup(name='ouroboros',
      version='0.1',
      author='shenely',
      description='A serpent eating its own tail',
      packages=['ouroboros.lib'],
      install_requires=['ob-core',
                        'ob-time',
                        'ob-math',
                        'ob-astro'])

