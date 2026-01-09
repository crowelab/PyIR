"""
Minimal setup.py for backward compatibility.
Modern installations should use pyproject.toml via pip install.
"""
from setuptools import setup
import sys
import os

# Read version from pyproject.toml if possible, otherwise use fallback
version = '1.6.3'

# Read dependencies from requirements.txt if it exists
install_requires = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt', 'r') as f:
        install_requires = [line.strip() for line in f
                          if line.strip() and not line.startswith('#')]
else:
    # Fallback to hardcoded dependencies if requirements.txt doesn't exist
    install_requires = ['tqdm']
    if sys.version_info < (3, 9):
        install_requires.append('importlib_resources>=1.3.0')

setup(
    name='crowelab_pyir',
    version=version,
    description='An IgBLAST wrapper and parser',
    license='Creative Commons Attribution 4.0',
    author='Sam Day, Andre Branchizio, Jordan Willis, Jessica Finn, Taylor Jones, Sam Schmitz, Luke Myers',
    author_email='samuel.day@vumc.org, andrejbranch@gmail.com, jwillis0720@gmail.com, strnad.bird@gmail.com',
    scripts=['./bin/pyir'],
    install_requires=['tqdm'],
    packages=['crowelab_pyir'],
    package_dir={'crowelab_pyir': './pyir'},
    package_data={'crowelab_pyir': ['data/*',
                                'data/bin/*',
                                'data/crowelab_data/*',
                                'data/crowelab_data/*/*',
                                'data/crowelab_data/*/*/*',
                                'data/germlines/aux_data/*',
                                'data/germlines/internal_data/*',
                                'data/germlines/internal_data/*/*'
                                    ]
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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
