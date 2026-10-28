#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup, find_packages


VERSION = "1.0.0b2"

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
    'License :: OSI Approved :: MIT License',
]


setup(
    name='logicapp',
    version=VERSION,
    description='Manage Azure Logic Apps Standard projects, workflows, connections, local runtimes, and Stateful executions.',
    long_description='An Azure CLI extension for Logic Apps Standard developer workflows.',
    license='MIT',
    author='Microsoft Corporation',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/logicapp',
    classifiers=CLASSIFIERS,
    package_data={'azext_logicapp': ['azext_metadata.json']},
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    python_requires='>=3.10',
    # Later psutil releases require a source build on Windows x86. WOW64 reports
    # AMD64 too, so an architecture marker would not reliably preserve its wheel.
    install_requires=[
        "psutil>=5.9.0,<7.1.2; sys_platform == 'win32'",
        "psutil>=5.9.0; sys_platform != 'win32'",
    ]
)
