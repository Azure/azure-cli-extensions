#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
import os
from setuptools import setup, find_packages
try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")

VERSION = '1.7.1'

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

DEPENDENCIES = []

# Get absolute path to the directory containing setup.py
HERE = os.path.abspath(os.path.dirname(__file__))

# Use absolute paths to read the files
with open(os.path.join(HERE, 'README.rst'), 'r', encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(HERE, 'HISTORY.rst'), 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='fleet',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools Fleet Extension',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/fleet',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_fleet': ['azext_metadata.json']},
)
