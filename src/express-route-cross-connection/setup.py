#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages

VERSION = "0.1.0"

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
    name='express-route-cross-connection',
    version=VERSION,
    description='Manage customer ExpressRoute circuits using an ExpressRoute cross-connection.',
    long_description='These commands give ISPs limited ability to manage the ExpressRoute circuits of ' \
                     'their customers through an ExpressRoute cross-connection resource.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/express-route-cross-connection',
    classifiers=CLASSIFIERS,
    package_data={'azext_expressroutecrossconnection': ['azext_metadata.json']},
    packages=find_packages(),
    install_requires=DEPENDENCIES
)
