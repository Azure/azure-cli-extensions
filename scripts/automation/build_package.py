#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import argparse
import os
import glob
from subprocess import check_call

DEFAULT_DEST_FOLDER = "./dist"

# A package declares its build through either a pyproject.toml or a legacy setup.py.
BUILD_FILES = ('pyproject.toml', 'setup.py')

def create_package(name, dest_folder=DEFAULT_DEST_FOLDER):
    # a package will exist in either one, or the other folder. this is why we can resolve both at the same time.
    absdirs = [
        os.path.dirname(package)
        for build_file in BUILD_FILES
        for package in (glob.glob('{}/{}'.format(name, build_file)) + glob.glob('sdk/*/{}/{}'.format(name, build_file)))
    ]
    if not absdirs:
        raise RuntimeError("Unable to locate a buildable package for {}: "
                           "no pyproject.toml or setup.py found.".format(name))
    absdirpath = os.path.abspath(absdirs[0])
    check_call(['python', '-m', 'build', '--wheel', '--sdist', '--no-isolation', '--outdir', dest_folder], cwd=absdirpath)

if __name__ == '__main__':
    """
    This file is used for Swagger CLI extension automation to build the wheel file and zip file
    """
    parser = argparse.ArgumentParser(description='Build Azure package.')
    parser.add_argument('name', help='The package name')
    parser.add_argument('--dest', '-d', default=DEFAULT_DEST_FOLDER,
                        help='Destination folder. Relative to the package dir. [default: %(default)s]')
    args = parser.parse_args()
    create_package(args.name, args.dest)


