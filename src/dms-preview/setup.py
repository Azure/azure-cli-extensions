#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.12.0"

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

setup(
    name='dms-preview',
    version=VERSION,
    description='Support for new Database Migration Service scenarios.',
    license='MIT',
    author='Artyom Pavlichenko',
    author_email='arpavlic@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/dms-preview',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["test"]),
    package_data={'azext_dms': ['azext_metadata.json']},
    install_requires=DEPENDENCIES
)
