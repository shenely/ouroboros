from setuptools import setup

setup(name='ob-math',
      version='0.1',
      author='shenely',
      description='On the shoulders of giants',
      package_dir={'ouroboros.ext.math': 'ob-math',
                   'ouroboros.lib': 'lib',
                   'ouroboros.test': 'test'},
      packages=['ouroboros.ext.math',
                'ouroboros.lib',
                'ouroboros.test'],
      install_requires=['ouroboros'])

