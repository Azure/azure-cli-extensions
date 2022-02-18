#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.3.0"

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

setup(
    name='aem',
    version=VERSION,
    description='Manage Azure Enhanced Monitoring Extensions for SAP',
    long_description='N/A',
    license='MIT',
    author='Yugang Wang',
    author_email='yugangw@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/aem',
    classifiers=CLASSIFIERS,
    package_data={'azext_aem': ['azext_metadata.json']},
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
