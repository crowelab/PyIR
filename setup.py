#!/usr/bin env python
from distutils.core import setup

setup(
    name='pyir',
    version='1.3.1',
    description='',
    author='Sam Day, Andre Branchizio, Jordan Willis, Jessica Finn, Taylor Jones, Sam Schmitz',
    author_email='samuel.day@vumc.org, andrejbranch@gmail.com, jwillis0720@gmail.com, strnad.bird@gmail.com',
    scripts=['./bin/pyir'],
    install_requires=['tqdm'],
    packages=['pyir'],
    package_dir={'pyir': './pyir'},
    package_data={'pyir': ['pyir/*',
                                'pyir/data/*',
                                'pyir/data/bin/*',
                                'pyir/data/germlines/*',
                                'pyir/data/germlines/aux_data/*',
                                'pyir/data/germlines/Ig/human/*',
                                'pyir/data/germlines/internal_data/human/*',
                                'pyir/data/germlines/TCR/human/*']
                  },
    include_package_data=True
)
