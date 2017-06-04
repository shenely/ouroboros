from setuptools import setup

setup(name='ob-math',
      version='0.1',
      author='shenely',
      description='On the shoulders of giants',
      package_dir={'ouroboros.lib': 'src'},
      packages=['ouroboros.lib'],
      install_requires=['ob-core'])

