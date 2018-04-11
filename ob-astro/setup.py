from setuptools import setup, Extension

libunikep = Extension('libunikep',
                      include_dirs=['include'],
                      sources=['lib/unikep.c'])
liborbele = Extension('liborbele',
                      include_dirs=['include'],
                      sources=['lib/orbele.c'])

setup(name='ob-astro',
      version='0.1',
      author='shenely',
      description='Circles within circles',
      package_dir={'ouroboros.lib': 'src',
                   'ouroboros.ext': 'lib',
                   'ouroboros.test': 'test'},
      packages=['ouroboros.lib',
                'ouroboros.ext',
                'ouroboros.test'],
      ext_package='ouroboros.ext',
      ext_modules=[libunikep,
                   liborbele],
      install_requires=['ob-core',
                        'ob-time',
                        'numpy',
                        'scipy',
                        'sgp4'])

