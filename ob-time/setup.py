from setuptools import setup

setup(name='ob-time',
      version='0.1',
      author='shenely',
      description='A brief history',
      package_dir={'ouroboros.ext': 'ob-time'},
      packages=['ouroboros.ext'],
      install_requires=['ob-core',
                        'pytz'])

