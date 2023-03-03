#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages
import stat
import requests
import os

try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger

    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# TODO: Confirm this is the right version number you want and it matches your
# HISTORY.rst entry.
VERSION = "0.2.11"

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

DEPENDENCIES = ["docker", "tqdm", "deepdiff"]

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "azext_confcom")

bin_folder = dir_path + "/bin"
if not os.path.exists(bin_folder):
    os.makedirs(bin_folder)

exe_path = dir_path + "/bin/dmverity-vhd.exe"
if not os.path.exists(exe_path):
    r = requests.get("https://github.com/microsoft/hcsshim/releases/download/v0.10.0-rc.6/dmverity-vhd.exe")
    with open(exe_path, "wb") as f:
        f.write(r.content)

bin_path = dir_path + "/bin/dmverity-vhd"
if not os.path.exists(bin_path):
    r = requests.get("https://github.com/microsoft/hcsshim/releases/download/v0.10.0-rc.6/dmverity-vhd")
    with open(bin_path, "wb") as f:
        f.write(r.content)

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
            "bin/dmverity-vhd.exe",  # windows
            "bin/dmverity-vhd",  # linux
            "data/*",
        ]
    },
)
