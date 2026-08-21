#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import find_packages, setup

VERSION = "0.1.0"

with open("README.rst", "r", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.rst", "r", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name="edgeoperator",
    version=VERSION,
    description="Microsoft Azure Command-Line Tools ALDO Extension",
    author="Microsoft Corporation",
    author_email="azpycli@microsoft.com",
    url="https://github.com/Azure/azure-cli-extensions/tree/main/src/edgeoperator",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    package_data={"azext_edgeoperator": ["azext_metadata.json"]},
)
