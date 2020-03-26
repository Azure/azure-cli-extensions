#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.1.6"

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

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='application-insights',
    version=VERSION,
    description='Support for managing Application Insights components and querying metrics, events, and logs from such components.',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    author='Ace Eldeib',
    author_email='aleldeib@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/application-insights',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["tests"]),
    package_data={'azext_applicationinsights': ['azext_metadata.json']},
    install_requires=DEPENDENCIES
)
