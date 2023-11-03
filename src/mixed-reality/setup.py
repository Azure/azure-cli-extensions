#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.0.5"

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
    name='mixed-reality',
    version=VERSION,
    description='Mixed Reality Azure CLI Extension.',
    long_description='Azure CLI Extension of Mixed Reality Azure Resource Management',
    license='MIT',
    author='Xiangyu Luo',
    author_email='xiangyul@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/mixed-reality',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES,
    package_data={
        'azext_mixed_reality': [
            'azext_metadata.json'
        ]
    }
)
