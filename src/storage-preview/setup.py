#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.2.5"

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
    name='storage-preview',
    version=VERSION,
    description='Provides a preview for upcoming storage features.',
    long_description='An Azure CLI Extension for storage preview features. This will replace the full storage module.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/storage-preview',
    classifiers=CLASSIFIERS,
    package_data={
        'azext_storage_preview': ['azext_metadata.json', 'azcopy/*/*']
    },
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
