#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set up for olx-utils"""

import os
import os.path
from setuptools import setup


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
    use_scm_version=True,
    description='Utilities for edX OLX courses',
    long_description=open('README.rst').read(),
    url='https://github.com/hastexo/olx-utils',
    author='hastexo',
    author_email='pypi@hastexo.com',
    license='AGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Education',
    ],
    packages=['olxutils'],
    install_requires=[
        'Mako>=1.0.3',
        'markdown2>=2.3.0',
        'Pygments>=2.0.1',
        'python-swiftclient>=2.2.0',
        'requests',
        'xmltodict',
    ],
    entry_points={
        'console_scripts': [
            'olx=olxutils.cli:main',
            'olx-new-run=olxutils.cli:main',
            'new_run.py=olxutils.cli:main',
        ],
    },
    package_data=package_data("olxutils", ["templates"]),
    setup_requires=['setuptools-scm'],
)
