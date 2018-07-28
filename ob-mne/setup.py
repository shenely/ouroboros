from setuptools import setup

setup(name='ob-mne',
      version='0.1',
      author='shenely',
      description='Something something dark side',
      package_dir={'ouroboros.ext': 'ob-mne'},
      packages=['ouroboros.ext'],
      install_requires=['ob-core'])

