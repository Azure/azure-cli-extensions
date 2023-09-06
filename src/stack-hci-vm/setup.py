#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
from codecs import open
from setuptools import setup, find_packages

# HISTORY.rst entry.
VERSION = '0.2.9'
try:
    from azext_azurestackhci.manual.version import VERSION
except ImportError:
    pass

if '--version' in sys.argv:
    index = sys.argv.index('--version')
    sys.argv.pop(index)  # Removes the '--version'
    VERSION = sys.argv.pop(index)  # Returns the element after the '--version'
# The version is now ready to use for the setup

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
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

try:
    from azext_azurestackhci.manual.dependency import DEPENDENCIES
except ImportError:
    pass

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='azurestackhci',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools AzureStackHCI Extension',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/azurestackhci',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_azurestackhci': ['azext_metadata.json']},
)
