#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = "0.1.0"

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

DEPENDENCIES = [
    'paramiko==2.6.0',
    'cryptography==2.8.0'
]

setup(
    name='ssh',
    version=VERSION,
    description='SSH into VMs',
    long_description='SSH into VMs using RBAC',
    license='MIT',
    author='Ryan Rossiter',
    author_email='ryrossit@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/ssh',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_ssh': ['azext_metadata.json']}
)
