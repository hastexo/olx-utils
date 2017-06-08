#!/usr/bin/env python
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
    version='0.0.8',
    description='Utilities for edX OLX courses',
    url='https://github.com/hastexo/olx-utils',
    author='hastexo',
    author_email='pypi@hastexo.com',
    license='AGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Education',
    ],
    packages=['olxutils'],
    install_requires=[
        'Mako>=1.0.3',
        'markdown2>=2.3.0',
        'Pygments>=2.0.1',
        'python-swiftclient>=2.2.0',
    ],
    scripts=package_scripts(["bin"]),
    package_data=package_data("olxutils", ["templates"]),
)
