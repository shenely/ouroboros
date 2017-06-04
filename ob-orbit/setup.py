from setuptools import setup

setup(name='ob-orbit',
      version='0.1',
      author='shenely',
      description='Circles within circles',
      package_dir={'ouroboros.lib': 'src'},
      py_modules=['ouroboros.lib.geo',
                  'ouroboros.lib.orb'],
      install_requires=['ob-core',
                        'numpy>=1.11',
                        'scipy>0.18',
                        'sgp4>=1.4'])

