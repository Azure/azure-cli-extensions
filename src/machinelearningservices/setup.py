#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from io import open
from setuptools import setup, find_packages

# HISTORY.rst entry.
VERSION = '2.39.0'

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Environment :: Console',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

try:
    from azext_mlv2.manual.dependency import DEPENDENCIES
except ImportError:
    pass

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()
with open("CHANGELOG.rst", encoding="utf-8") as f:
    changelog = f.read()

setup(
    name='ml',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools AzureMachineLearningWorkspaces Extension',
    long_description_content_type="text/x-rst",
    long_description=readme + '\n\n' + changelog,
    author='Microsoft Corporation',
    author_email='azuremlsdk@microsoft.com',
    url='https://docs.microsoft.com/azure/machine-learning/azure-machine-learning-release-notes-cli-v2?view=azureml-api-2',
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_mlv2': ['azext_metadata.json']},
)
