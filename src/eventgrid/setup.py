#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.4.4"

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
    name='eventgrid',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools EventGrid Command Module.',
    long_description='Support for Azure EventGrid features in 2020-01-01-preview API version.',
    license='MIT',
    author='Ashraf Hamad.',
    author_email='ahamad@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["tests"]),
    package_data={'azext_eventgrid': ['azext_metadata.json']},
    install_requires=DEPENDENCIES
)
