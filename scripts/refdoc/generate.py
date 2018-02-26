# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import copy
import shutil
import argparse
import tempfile
import datetime
from subprocess import check_call, CalledProcessError


ENV_KEY_AZURE_EXTENSION_DIR = 'AZURE_EXTENSION_DIR'

def print_status(msg=''):
    print('-- '+msg)


def generate(ext_file, output_dir):
    # Verify sphinx installed in environment before we get started
    check_call(['sphinx-build', '--version'])
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix='ref-doc-out-', dir=os.getcwd())
    print_status('Using output directory {}'.format(output_dir))
    temp_extension_dir = tempfile.mkdtemp()
    try:
        pip_cmd = [sys.executable, '-m', 'pip', 'install', '--target', os.path.join(temp_extension_dir, 'extension'),
                   ext_file, '--disable-pip-version-check', '--no-cache-dir']
        print_status('Executing "{}"'.format(' '.join(pip_cmd)))
        check_call(pip_cmd)
        # TODO-DEREK Check these. It's running the correct script?
        sphinx_cmd = ['sphinx-build', '-b', 'xml', os.path.dirname(os.path.realpath(__file__)), output_dir]
        env = copy.copy(os.environ)
        env[ENV_KEY_AZURE_EXTENSION_DIR] = temp_extension_dir
        print_status('Executing "{}" with {} set to {}'.format(' '.join(sphinx_cmd),
                                                               ENV_KEY_AZURE_EXTENSION_DIR,
                                                               env['AZURE_EXTENSION_DIR']))
        check_call(sphinx_cmd, env=env)
    finally:
        shutil.rmtree(temp_extension_dir)
        print_status('Cleaned up temp directory {}'.format(temp_extension_dir))
    print_status('Ref doc output available at {}'.format(output_dir))
    print_status('Done.')


def _type_ext_file(val):
    ext_file = os.path.realpath(os.path.expanduser(val))
    if os.path.isdir(ext_file):
        raise argparse.ArgumentTypeError('{} is a directory not an extension file.'.format(ext_file))
    if not os.path.isfile(ext_file):
        raise argparse.ArgumentTypeError('{} does not exist.'.format(ext_file))
    if os.path.splitext(ext_file)[1] != '.whl':
        raise argparse.ArgumentTypeError('{} Extension files should end with .whl'.format(ext_file))
    return ext_file


def _type_path(val):
    out_path = os.path.realpath(os.path.expanduser(val))
    if not os.path.isdir(out_path):
        raise argparse.ArgumentTypeError('{} is not a directory. Create it or specify different directory.'.format(out_path))
    if os.listdir(out_path):
        raise argparse.ArgumentTypeError('{} is not empty. Empty output directory required.'.format(out_path))
    return out_path


# A small command line interface for the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to generate reference documentation for a single Azure CLI extension.')

    parser.add_argument('-e', '--extension-file', dest='ext_file',
                        help='Path to the extension .whl file.', required=True, type=_type_ext_file)
    parser.add_argument('-o', '--output-dir', dest='output_dir',
                        help='Path to place the generated documentation. By default, a temporary directory will be created.', required=False, type=_type_path)

    args = parser.parse_args()
    generate(args.ext_file, args.output_dir)
