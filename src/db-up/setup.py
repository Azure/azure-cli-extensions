#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.1.12"

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
    'Cython==0.29.6',
    'mysql-connector-python==8.0.13',
    'psycopg2-binary==2.7.7'
]

setup(
    name='db-up',
    version=VERSION,
    description='Additional commands to simplify Azure Database workflows.',
    long_description='An Azure CLI Extension to provide additional DB commands.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/db-up',
    classifiers=CLASSIFIERS,
    package_data={'azext_db_up': ['azext_metadata.json', 'random_name/*']},
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
