#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from io import open
from setuptools import setup, find_packages

VERSION = "3.0.0"

with open('README.md', encoding='utf-8') as f:
    readme = f.read()
with open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()

setup(
    name='vmware',
    version=VERSION,
    description='Azure VMware Solution commands.',
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Microsoft',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/az-vmware-cli',
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    package_data={'azext_vmware': ['azext_metadata.json']}
)
