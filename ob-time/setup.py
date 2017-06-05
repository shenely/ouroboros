from setuptools import setup

setup(name='ob-time',
      version='0.1',
      author='shenely',
      description='A brief history',
      package_dir={'ouroboros.lib': 'src'},
      packages=['ouroboros.lib'],
      install_requires=['ob-core',
                        'pytz'])

