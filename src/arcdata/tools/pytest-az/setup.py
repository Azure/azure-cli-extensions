#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from codecs import open
from setuptools import setup

import os


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
REQUIREMENTS = os.path.expandvars(read("requirements.txt"))
README = read("README.rst")
HISTORY = read("HISTORY.rst")
ABOUT = {}
exec(read(os.path.join("__version__.py")), ABOUT)


setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    license=ABOUT["__license__"],
    description=ABOUT["__description__"],
    long_description=README + "\n\n" + HISTORY,
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    keywords=ABOUT["__keywords__"],
    py_modules=["pytest_az"],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    entry_points={"pytest11": ["az = pytest_az"]},
)
