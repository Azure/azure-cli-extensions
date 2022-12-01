#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from get_python_version import get_all_tests, get_min_version, run_command
from util import SRC_PATH
import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

ALL_TESTS = []
EXTENSION_NAME, ORIGINAL_EXTENSION_NAME = '', ''


def prepare_for_min_version(min_version):
    logger.info(f'checkout to minCliCoreVersion: {min_version}')
    az_min_version = 'azure-cli-' + min_version
    azure_cli_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(SRC_PATH))), 'azure-cli')
    # checkout to min cli version
    cmd = ['git', 'checkout', az_min_version]
    run_command(cmd, check_return_code=True, cwd=azure_cli_path)
    # display cli version
    cmd = ['az', '--version']
    run_command(cmd, check_return_code=True)
    logger.info('installing old testsdk')
    testsdk_path = os.path.join(azure_cli_path, 'src', 'azure-cli-testsdk')
    cmd = ['python', 'setup.py', 'install']
    run_command(cmd, check_return_code=True, cwd=testsdk_path)
    logger.info(f'installing extension: {ORIGINAL_EXTENSION_NAME}')
    cmd = ['azdev', 'extension', 'add', ORIGINAL_EXTENSION_NAME]
    run_command(cmd, check_return_code=True)


def run_tests():
    cmd = ['azdev', 'test', ORIGINAL_EXTENSION_NAME, '--no-exitfirst', '--verbose']
    return run_command(cmd, check_return_code=True)


def main():
    get_all_tests()
    min_version = get_min_version()
    prepare_for_min_version(min_version)
    sys.exit(1) if run_tests() else sys.exit(0)


if __name__ == '__main__':
    main()
