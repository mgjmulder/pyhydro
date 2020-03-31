from setuptools import setup

setup(name='pyhydro',
      version='0.2',
      description='Hydrology toolbox of Vitens',
      url='https://github.com/Vitens/pyhydro/',
      author='Martijn Mulder',
      author_email='martijn.mulder@vitens.nl',
      packages=['pyhydro'],
      install_requires=['datetime',
			'geopandas',
                        'numpy',
                        'pandas',
                        'shapely',
			'pylizard @ git+https://github.com/Vitens/pylizard.git'],
      zip_safe=False)