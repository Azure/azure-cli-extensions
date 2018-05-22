#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

VERSION = "0.1.1"

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
    name='dev-spaces-preview',
    version=VERSION,
    description='Dev Spaces provides a rapid, iterative Kubernetes development experience for teams.',
    long_description='Iteratively develop and debug containers in a Azure Kubernetes Service cluster using Dev Spaces. \
    Share an AKS cluster with your team and collaborate together. You can test code end-to-end without replicating or \
    mocking up dependencies. Onboard new team members faster by minimizing their local dev machine setup and have them \
    work in a consistent dev environment.',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azds-azcli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    package_data={'azext_dev_spaces_preview': ['azext_metadata.json']},
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
