#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from codecs import open
from setuptools import setup, find_packages
try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# Inspired by https://github.com/Azure/azure-cli-extensions/blob/63f9cca19ab7a163c6c368b8c62f9c32432a899c/src/alias/setup.py#L14
extension_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(extension_path, 'azext_ai_did_you_mean_this', 'version.py'), 'r') as version_file:
    VERSION = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        version_file.read(), re.MULTILINE).group(1)

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
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

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='ai_did_you_mean_this',
    version=VERSION,
    description='Recommend recovery options on failure.',
    # TODO: Update author and email, if applicable
    author="Christopher O'Toole",
    author_email='chotool@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/master/src/ai-did-you-mean-this',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_ai_did_you_mean_this': ['azext_metadata.json']},
)
