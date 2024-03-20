#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = "2.0.3"

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
    'oschmod==0.3.12'
]

setup(
    name='ssh',
    version=VERSION,
    description='SSH into Azure VMs using RBAC and AAD OpenSSH Certificates',
    long_description='SSH into Azure VMs using RBAC and AAD OpenSSH Certificates.  The client generates (or uses existing) OpenSSH keys that are then signed by AAD into OpenSSH certificates for access to Azure VMs with the AAD Extension installed.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/ssh',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_ssh': ['azext_metadata.json']}
)
