from setuptools import setup

setup(name='ob-orbit',
      version='0.1',
      author='shenely',
      description='Circles within circles',
      package_dir={'ouroboros.lib': 'src'},
      packages=['ouroboros.lib'],
      install_requires=['ob-core',
                        'numpy',
                        'scipy'])

