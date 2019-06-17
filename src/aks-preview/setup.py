#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open as open1
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

with open1('README.md', 'r', encoding='utf-8') as f:
    README = f.read()
with open1('HISTORY.md', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='aks-preview',
    version=VERSION,
    description='Provides a preview for upcoming AKS features',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/aks-preview',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["tests"]),
    package_data={'azext_aks_preview': ['azext_metadata.json']},
    install_requires=DEPENDENCIES
)
