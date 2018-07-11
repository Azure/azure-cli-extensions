#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.0.7"

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
    name='express-route-cross-connection',
    version=VERSION,
    description='Support for ExpressRoute cross connection resources',
    long_description='Support for ExpressRoute cross connection resources',
    license='MIT',
    author='Travis Prescott',
    author_email='trpresco@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    package_data={'azext_express-route-cross-connection': ['azext_metadata.json']},
    packages=find_packages(),
    install_requires=DEPENDENCIES
)
