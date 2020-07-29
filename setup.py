from setuptools import setup

setup(name='pyhydro',
      version='0.4',
      description='Hydrology toolbox of Vitens',
      url='https://github.com/Vitens/pyhydro/',
      author='Martijn Mulder',
      author_email='martijn.mulder@vitens.nl',
      packages=['pyhydro'],
      install_requires=['datetime',
			            'geopandas',
			'matplotlib',
                        'imod',
                        'numpy',
                        'pandas',
                        'shapely'],
      zip_safe=False)