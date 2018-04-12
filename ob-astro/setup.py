from setuptools import setup, Extension

libunikep = Extension('_libunikep',
                      include_dirs=['include'],
                      sources=['src/unikep.c'])
liborbele = Extension('_liborbele',
                      include_dirs=['include'],
                      sources=['src/orbele.c'])

setup(name='ob-astro',
      version='0.1',
      author='shenely',
      description='Circles within circles',
      package_dir={'ouroboros.ext': 'ob-astro',
                   'ouroboros.lib': 'lib',
                   'ouroboros.test': 'test'},
      packages=['ouroboros.ext',
                'ouroboros.lib',
                'ouroboros.test'],
      ext_package='ouroboros.lib',
      ext_modules=[libunikep,
                   liborbele],
      install_requires=['ob-core',
                        'ob-time',
                        'numpy',
                        'scipy',
                        'sgp4'])

