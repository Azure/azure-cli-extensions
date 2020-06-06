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
    name='vm-repair',
    version=VERSION,
    description='Auto repair commands to fix VMs.',
    long_description='VM repair scripts will enable Azure users to self-repair non-connectable VMs by copying the source VM\'s OS disk and attaching it to a newly created repair VM.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='caiddev@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/vm-repair',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    package_data={'azext_vm_repair': ['scripts/linux-run-driver.sh', 'scripts/win-run-driver.ps1', 'scripts/mount-encrypted-disk.sh']},
    install_requires=DEPENDENCIES
)
