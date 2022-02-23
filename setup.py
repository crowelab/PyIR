#!/usr/bin env python
from distutils.core import setup

setup(
    name='crowelab_pyir',
    version='1.5.0',
    description='',
    license='Creative Commons Attribution 4.0',
    author='Sam Day, Andre Branchizio, Jordan Willis, Jessica Finn, Taylor Jones, Sam Schmitz',
    author_email='samuel.day@vumc.org, andrejbranch@gmail.com, jwillis0720@gmail.com, strnad.bird@gmail.com',
    scripts=['./bin/pyir'],
    install_requires=['tqdm'],
    packages=['crowelab_pyir'],
    package_dir={'crowelab_pyir': './pyir'},
    package_data={'crowelab_pyir': ['data/*',
                                'data/bin/*',
                                'data/germlines/*',
                                'data/germlines/aux_data/*',
                                'data/germlines/Ig/human/*',
                                'data/germlines/prot/human/*'
                                'data/germlines/internal_data/*',
                                'data/germlines/internal_data/*/*',
                                'data/germlines/TCR/human/*']
                  },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
