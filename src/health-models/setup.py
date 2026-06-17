# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open  # pylint: disable=redefined-builtin
from setuptools import setup, find_packages

VERSION = '1.0.0b1'

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
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='health-models',
    version=VERSION,
    description='Support for managing Azure Monitor Health Models, including entities, signals, relationships, authentication settings, and discovery rules.',
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/health-models',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_health_models': ['azext_metadata.json']},
    python_requires='>=3.10',
)
