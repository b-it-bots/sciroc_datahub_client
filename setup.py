#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# for your packages to be recognized by python
d = generate_distutils_setup(
    packages=['sciroc_datahub_client'], 
    package_dir={'sciroc_datahub_client': 'common/sciroc_datahub_client'}
)

setup(**d)
