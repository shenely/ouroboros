from setuptools import setup

setup(name='ob-time',
      version='0.1',
      author='shenely',
      description='A brief history',
      package_dir={'ouroboros.ext.time': 'ob-time'},
      packages=['ouroboros.ext.time'],
      install_requires=['ouroboros',
                        'pytz'])

