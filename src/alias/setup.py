#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from setuptools import setup, find_packages

# Inspired by https://github.com/Azure/azure-sdk-for-python/blob/master/azure-mgmt-cdn/setup.py#L45
extension_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(extension_path, 'azext_alias', 'version.py'), 'r') as version_file:
    VERSION = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        version_file.read(), re.MULTILINE).group(1)

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

DEPENDENCIES = [
    'jinja2~=2.10'
]

setup(
    name='alias',
    version=VERSION,
    description='Support for command aliases',
    long_description='An Azure CLI extension that provides command aliases functionality',
    license='MIT',
    author='Ernest Wong',
    author_email='t-chwong@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    package_data={'azext_alias': ['azext_metadata.json']},
    packages=find_packages(exclude=["azext_alias.tests"]),
    install_requires=DEPENDENCIES
)
