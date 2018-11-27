#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

DEPENDENCIES = [
    'pyyaml'
]

setup(
    name='sfmergeutility',
    version='0.1.4',
    packages=find_packages(exclude=("tests",)),
    license='MIT',
    description='Service Fabric Yaml merge utility',
    install_requires=DEPENDENCIES,
    url='https://github.com/Azure/azure-cli-extensions',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    package_data={'sfmergeutility': ['settings.json']},
    include_package_data=True,
)