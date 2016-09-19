# -*- coding: utf-8 -*-
"""Set up for olx-utils"""

import os
import os.path
from setuptools import setup

def package_scripts(root_list):
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(root):
            for fname in files:
                data.append(os.path.join(dirname, fname))
    return data

def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

setup(
    name='olx-utils',
    version='0.0.2',
    description='Utilities for edX OLX courses',
    packages=['olxutils'],
    install_requires=[
        'Mako>=1.0.3',
        'markdown2>=2.3.0',
        'Pygments>=2.0.1',
    ],
    scripts=package_scripts(["bin"]),
    package_data=package_data("olxutils", ["templates"]),
)
