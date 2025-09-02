#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open as open1

from setuptools import find_packages, setup

VERSION = "1.0.0b1"

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
]

DEPENDENCIES = [
    "holmesgpt==0.12.6; python_version >= '3.10'",
]

with open1("README.rst", "r", encoding="utf-8") as f:
    README = f.read()
with open1("HISTORY.rst", "r", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name="aks-agent",
    version=VERSION,
    description="Provides an interactive AI-powered debugging tool for AKS",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    author="Microsoft Corporation",
    author_email="azpycli@microsoft.com",
    url="https://github.com/Azure/azure-cli-extensions/tree/main/src/aks-agent",
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["tests"]),
    package_data={"azext_aks_agent": ["azext_metadata.json"]},
    install_requires=DEPENDENCIES,
)
