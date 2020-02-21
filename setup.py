from setuptools import setup

setup(name='pyhydro',
      version='0.1',
      description='Hydrology toolbox of Vitens',
      url='https://github.com/Vitens/pyhydro/',
      author='Martijn Mulder',
      author_email='martijn.mulder@vitens.nl',
      packages=['pyhydro'],
      install_requires=['geopandas',
                        'numpy',
                        'pandas',
                        'shapely',
                        'time'],
      zip_safe=False)