# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from setuptools import setup, find_packages


VERSION = "1.0.1"
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
    name='maintenance',
    version=VERSION,
    description='Support for Azure maintenance management.',
    long_description='Microsoft Azure Command-Line Extensions for Maintenance',
    license='MIT',
    author='Abhishek Kumar',
    author_email='abkmr@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    package_data={'azext_maintenance': ['azext_metadata.json']},
    packages=find_packages(exclude=['tests']),
    install_requires=DEPENDENCIES
)
