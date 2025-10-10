# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os
from codecs import open
from setuptools import setup, find_packages


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


def read(file):
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(cwd, file), "r", "utf-8") as f:
        return f.read()


CLASSIFIERS = [
    "Development Status :: 1 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
]

REQUIREMENTS = os.path.expandvars(read(os.path.join("requirements.txt")))
README = read("README.rst")
HISTORY = read("HISTORY.rst")
ABOUT = {}
exec(read(os.path.join("azext_arcdata", "__version__.py")), ABOUT)

setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    license=ABOUT["__license__"],
    description=ABOUT["__description__"],
    long_description=README + "\n\n" + HISTORY,
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    classifiers=CLASSIFIERS,
    package_data={"azext_arcdata": ["azext_metadata.json"]},
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    install_requires=REQUIREMENTS,
    include_package_data=True,
)
