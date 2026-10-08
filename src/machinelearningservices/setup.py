#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
import os
from io import open
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

# HISTORY.rst entry.
VERSION = '2.45.1'

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Environment :: Console',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

try:
    from azext_mlv2.manual.dependency import DEPENDENCIES
except ImportError:
    pass

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()
with open("CHANGELOG.rst", encoding="utf-8") as f:
    changelog = f.read()


class BuildPyWithExtensionMetadata(build_py):
    def run(self):
        super().run()
        self.execute(self._write_extension_metadata, (), "Writing Azure CLI extension identity metadata")

    def _write_extension_metadata(self):
        metadata_path = os.path.join(self.build_lib, "azext_mlv2", "azext_metadata.json")
        with open(metadata_path, encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        # Older CLI pkginfo versions cannot read metadata emitted by modern setuptools.
        metadata["name"] = self.distribution.get_name()
        metadata["version"] = self.distribution.get_version()
        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=2)
            metadata_file.write("\n")


setup(
    name='ml',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools AzureMachineLearningWorkspaces Extension',
    long_description_content_type="text/x-rst",
    long_description=readme + '\n\n' + changelog,
    author='Microsoft Corporation',
    author_email='azuremlsdk@microsoft.com',
    url='https://docs.microsoft.com/azure/machine-learning/azure-machine-learning-release-notes-cli-v2?view=azureml-api-2',
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    package_data={'azext_mlv2': ['azext_metadata.json']},
    cmdclass={'build_py': BuildPyWithExtensionMetadata},
)
