from setuptools import setup

setup(name='ob-sat',
      version='0.1',
      author='shenely',
      description='It\'s not brain surgery',
      package_dir={'ouroboros.ext.sat': 'ob-sat'},
      packages=['ouroboros.ext.sat'],
      install_requires=['ouroboros',
                        'ob-time',
                        'ob-astro',
                        'ob-data',
                        'numpy'])

