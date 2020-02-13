#!/usr/bin env python
from distutils.core import setup

setup(
    name='pyir',
    version='0.2.0',
    description='',
    author='Sam Day, Andre Branchizio, Jordan Willis, Jessica Finn, Taylor Jones, Sam Schmitz',
    author_email='andrejbranch@gmail.com, jwillis0720@gmail.com, strnad.bird@gmail.com, samuel.day@gmail.com',
    scripts=['./bin/pyir'],
    install_requires=['tqdm'],
    packages=['PyIR'],
    package_dir={'PyIR': './PyIR'},
    package_data={'PyIR': ['PyIR/*',
                                'PyIR/data/*',
                                'PyIR/data/bin/*',
                                'PyIR/data/germlines/*',
                                'PyIR/data/germlines/aux_data/*',
                                'PyIR/data/germlines/Ig/human/*',
                                'PyIR/data/germlines/internal_data/human/*',
                                'PyIR/data/germlines/TCR/human/*']
                  },
    include_package_data=True
)
