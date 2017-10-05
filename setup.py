#!/usr/bin env python
from distutils.core import setup

setup(
    name='pyir',
    version='1.0',
    description='Python Immunoglobulin Analysis Tool',
    author='Andre Branchizio, Jordan Willis, Jessica Finn',
    author_email='andrejbranch@gmail.com, jwillis0720@gmail.com, strnad.bird@gmail.com',
    packages=['pyir'],
    scripts=['bin/pyir'],
    install_requires=['biopython', 'tqdm'],
    package_data={'pyir': ['igblast/*', 'data_dir/aux/*', 'data_dir/**/**/*']},
    include_package_data = True
)
