#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from codecs import open
from setuptools import find_packages, setup

try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger

    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# Confirm this is the right version number you want and it matches your
# HISTORY.rst entry.
VERSION = "1.0.0b4"


# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
]

DEPENDENCIES = ["oras~=0.1.19", "jinja2>=3.1.2"]

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.rst", "r", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name="aosm",
    version=VERSION,
    description="Microsoft Azure Command-Line Tools Aosm Extension",
    author="Microsoft Corporation",
    author_email="azpycli@microsoft.com",
    url="https://github.com/Azure/azure-cli-extensions/tree/master/src/aosm",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={
        "azext_aosm": [
            "azext_metadata.json",
            "generate_nfd/templates/*",
            "generate_nsd/templates/*",
        ]
    },
)
