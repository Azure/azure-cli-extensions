#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.5.9"

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

with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='vm-repair',
    version=VERSION,
    description='Auto repair commands to fix VMs.',
    long_description='VM repair command will enable Azure users to self-repair non-bootable VMs by copying the source VM\'s OS disk and attaching it to a newly created repair VM.' + '\n\n' + HISTORY,
    license='MIT',
    author='Microsoft Corporation',
    author_email='caiddev@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/vm-repair',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    package_data={
        'azext_vm_repair': [
            'scripts/linux-run-driver.sh',
            'scripts/win-run-driver.ps1',
            'scripts/enable-nestedhyperv.ps1',
            'scripts/linux-mount-encrypted-disk.sh',
            'scripts/win-mount-encrypted-disk.ps1',
            'scripts/linux-build_setup-cloud-init.txt',
            'azext_metadata.json'
        ]
    },
    install_requires=DEPENDENCIES
)
