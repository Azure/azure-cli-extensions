#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages

import os
import platform
import requests

try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# TODO: Confirm this is the right version number you want and it matches your
# HISTORY.rst entry.

VERSION = '0.3.28'

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
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
]

# TODO: Add any additional SDK dependencies here
DEPENDENCIES = [
    'pycomposefile>=0.0.29',
    'docker'
]

# Install pack CLI to build runnable application images from source
try:
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "azext_containerapp")
    bin_folder = dir_path + "/bin"
    if not os.path.exists(bin_folder):
        os.makedirs(bin_folder)

    exec_name = ""
    host_os = platform.system()
    if host_os == "Windows":
        exec_name = "pack-v0.29.0-windows.exe"
    elif host_os == "Linux":
        exec_name = "pack-v0.29.0-linux"
    elif host_os == "Darwin":
        exec_name = "pack-v0.29.0-macos"
    else:
        raise Exception(f"Unsupported host OS: {host_os}")

    exec_path = os.path.join(bin_folder, exec_name)
    if not os.path.exists(exec_path):
        url = f"https://cormteststorage.blob.core.windows.net/pack/{exec_name}"
        r = requests.get(url)
        with open(exec_path, "wb") as f:
            f.write(r.content)
            print(f"Successfully installed pack CLI to {exec_path}\n")

except Exception as e:
    # Swallow any exceptions thrown when attempting to install pack CLI
    print(f"Failed to install pack CLI: {e}\n")

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='containerapp',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools Containerapp Extension',
    # TODO: Update author and email, if applicable
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    # TODO: consider pointing directly to your source code instead of the generic repo
    url='https://github.com/Azure/azure-cli-extensions',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_containerapp': ['azext_metadata.json']},
)
