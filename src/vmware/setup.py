#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from io import open
from setuptools import setup, find_packages

VERSION = "6.0.1"

with open('README.md', encoding='utf-8') as f:
    readme = f.read()
with open('HISTORY.md', encoding='utf-8') as f:
    history = f.read()

setup(
    name='vmware',
    version=VERSION,
    description='Azure VMware Solution commands.',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Microsoft',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/vmware',
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    package_data={'azext_vmware': ['azext_metadata.json']}
)
