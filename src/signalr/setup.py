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


setup(
    name='signalr',
    version=VERSION,
    description='Support for signalr management preview.',
    long_description='Microsoft Azure Command-Line Extensions for SignalR Service',
    license='MIT',
    author='Visual Studio China SignalR Team',
    author_email='vscsignalr@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions',
    classifiers=CLASSIFIERS,
    package_data={'azext_signalr': ['azext_metadata.json']},
    packages=find_packages(exclude=['tests'])
)
