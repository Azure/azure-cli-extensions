#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.1.0"

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

DEPENDENCIES = [
    'ddt~=1.1.1',
    'configparser~=3.5.0'
]

setup(
    name='alias',
    version=VERSION,
    description='Azure CLI Alias Extension',
    long_description='An Azure CLI extension that provides command alias functionality',
    license='MIT',
    author='Ernest Wong',
    author_email='t-chwong@microsoft.com',
    url='https://github.com/chewong/azure-cli-alias-extension',
    classifiers=CLASSIFIERS,
    package_data={'azext_alias': ['azext_metadata.json']},
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
