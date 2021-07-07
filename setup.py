#!/usr/bin env python
from distutils.core import setup

setup(
    name='pyir',
    version='1.4',
    description='',
    license='Creative Commons Attribution 4.0',
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
                                'pyir/data/germlines/prot/human/*'
                                'pyir/data/germlines/internal_data/*',
                                'pyir/data/germlines/internal_data/*/*',
                                'pyir/data/germlines/TCR/human/*']
                  },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: Creative Commons Attribution 4.0',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
