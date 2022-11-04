#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import json
import subprocess
import sys
import shlex
from subprocess import check_output


from util import SRC_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


ALL_TESTS = []
EXTENSION_NAME, ORIGINAL_EXTENSION_NAME = '', ''


def get_all_tests():
    global ALL_TESTS, EXTENSION_NAME, ORIGINAL_EXTENSION_NAME
    for src_d in os.listdir(SRC_PATH):
        src_d_full = os.path.join(SRC_PATH, src_d)
        if not os.path.isdir(src_d_full):
            continue
        pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)

        # If running in Travis CI, only run tests for edited extensions
        commit_range = os.environ.get('TRAVIS_COMMIT_RANGE')
        if commit_range and not check_output(['git', '--no-pager', 'diff', '--name-only', commit_range, '--', src_d_full]):
            continue

        # Running in Azure DevOps
        cmd_tpl = 'git --no-pager diff --name-only origin/{commit_start} {commit_end} -- {code_dir}'
        ado_branch_last_commit = os.environ.get('ADO_PULL_REQUEST_LATEST_COMMIT')
        ado_target_branch = os.environ.get('ADO_PULL_REQUEST_TARGET_BRANCH')
        if ado_branch_last_commit and ado_target_branch:
            if ado_branch_last_commit == '$(System.PullRequest.SourceCommitId)':
                # default value if ADO_PULL_REQUEST_LATEST_COMMIT not set in ADO
                continue
            elif ado_target_branch == '$(System.PullRequest.TargetBranch)':
                # default value if ADO_PULL_REQUEST_TARGET_BRANCH not set in ADO
                continue
            else:
                cmd = cmd_tpl.format(commit_start=ado_target_branch, commit_end=ado_branch_last_commit, code_dir=src_d_full)
                if not check_output(shlex.split(cmd)):
                    continue

        # Find the package and check it has tests
        test_dir = os.path.isdir(os.path.join(src_d_full, pkg_name, 'tests'))
        if pkg_name and test_dir:
            # [('azext_healthcareapis', '/mnt/vss/_work/1/s/src/healthcareapis')]
            ALL_TESTS.append((pkg_name, src_d_full))
            # azext_healthcareapis
            EXTENSION_NAME = ALL_TESTS[0][0]
            # healthcareapis
            _, ORIGINAL_EXTENSION_NAME = EXTENSION_NAME.split('_', 1)
        else:
            logger.error(f'can not any test in {test_dir}')
            sys.exit(0)

    # ALL_TESTS = [('azext_healthcareapis', 'C:\Code\Azure\azure-cli-extensions\src\healthcareapis')]
    # EXTENSION_NAME = ALL_TESTS[0][0]
    # _, ORIGINAL_EXTENSION_NAME = EXTENSION_NAME.split('_', 1)
    logger.warning(f'ado_branch_last_commit: {ado_branch_last_commit}, '
                   f'ado_target_branch: {ado_target_branch}, '
                   f'ALL_TESTS: {ALL_TESTS}.')


def get_min_version():
    try:
        with open(os.path.join(SRC_PATH, ORIGINAL_EXTENSION_NAME, EXTENSION_NAME, 'azext_metadata.json'), 'r') as f:
            min_version = json.load(f)['azext.minCliCoreVersion']
            logger.info(f'find min_version: {min_version}')
            return min_version
    except Exception as e:
        logger.error(f'can not get min_version: {e}')
        sys.exit(0)


def prepare_for_min_version(min_version):
    az_min_version = 'azure-cli-' + min_version
    azure_cli_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(SRC_PATH))), 'azure-cli')
    logger.info(f'azure_cli_path: {azure_cli_path}')
    cmd = ['git', 'checkout', az_min_version]
    run_command(cmd, check_return_code=True, cwd=azure_cli_path)
    cmd = ['az', '--version']
    run_command(cmd, check_return_code=True)
    # install old testsdk
    testsdk_path = os.path.join(azure_cli_path, 'src', 'azure-cli-testsdk')
    cmd = ['python', 'setup.py', 'install']
    run_command(cmd, check_return_code=True, cwd=testsdk_path)
    # azdev add extensions
    cmd = ['azdev', 'extension', 'add', ORIGINAL_EXTENSION_NAME]
    run_command(cmd, check_return_code=True)


def run_command(cmd, check_return_code=False, cwd=None):
    error_flag = False
    logger.info(cmd)
    try:
        out = subprocess.run(cmd, check=True, cwd=cwd)
        if check_return_code and out.returncode:
            raise RuntimeError(f"{cmd} failed")
    except subprocess.CalledProcessError:
        error_flag = True
    return error_flag


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
