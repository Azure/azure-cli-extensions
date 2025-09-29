#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages
from azext_confcom.rootfs_proxy import SecurityPolicyProxy
from azext_confcom.kata_proxy import KataPolicyGenProxy
from azext_confcom.cose_proxy import CoseSignToolProxy

try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger

    logger.warn("Wheel is not available, disabling bdist_wheel hook")

VERSION = "1.2.8"

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: MIT License",
]

DEPENDENCIES = [
    "docker>=6.1.0",
    "tqdm==4.65.0",
    "deepdiff==6.3.0",
    "PyYAML>=6.0.1"
]

SecurityPolicyProxy.download_binaries()
KataPolicyGenProxy.download_binaries()
CoseSignToolProxy.download_binaries()

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()
with open("HISTORY.rst", "r", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name="confcom",
    version=VERSION,
    description="Microsoft Azure Command-Line Tools Confidential Container Security Policy Generator Extension",
    author="Microsoft Corporation",
    author_email="acccli@microsoft.com",
    url="https://github.com/Azure/azure-cli-extensions/tree/main/src/confcom",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={
        "azext_confcom": [
            "azext_metadata.json",
            "bin/dmverity-vhd.exe",  # windows for ACI
            "bin/dmverity-vhd",  # linux for ACI
            "bin/genpolicy-windows.exe",  # windows for AKS
            "bin/genpolicy-linux",  # linux for AKS
            "bin/sign1util.exe",  # windows for cose tool
            "bin/sign1util",  # linux for cose tool
            "data/*",
        ]
    },
)
