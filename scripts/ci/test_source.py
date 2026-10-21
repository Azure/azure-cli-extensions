#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import logging
import os
import sys
import tempfile
import shutil
import shlex

from subprocess import check_output, CalledProcessError, run, STDOUT
from util import SRC_PATH

logger = logging.getLogger(__name__)

ALL_TESTS = []

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
    if pkg_name and os.path.isdir(os.path.join(src_d_full, pkg_name, 'tests')):
        ALL_TESTS.append((pkg_name, src_d_full))

logger.warning(f'ado_branch_last_commit: {ado_branch_last_commit}, '
               f'ado_target_branch: {ado_target_branch}, '
               f'ALL_TESTS: {ALL_TESTS}.')


def run_command(cmd, check_return_code=False, cwd=None):
    logger.info(f'cmd: {cmd}')
    out = run(cmd, check=True, cwd=cwd)
    if check_return_code and out.returncode:
        raise RuntimeError(f"{cmd} failed")


def test_extension():
    for pkg_name, ext_path in ALL_TESTS:
        ext_name = ext_path.split('/')[-1]
        logger.info(f'installing extension: {ext_name}')
        cmd = ['azdev', 'extension', 'add', ext_name]
        run_command(cmd, check_return_code=True)

        # Use azext_$ext_name, a unique long name for testing, to avoid the following error when the main module and extension name have the same name:
        # 'containerapp' exists in both 'azext_containerapp' and 'containerapp'. Resolve using `azext_containerapp.containerapp` or `containerapp.containerapp`
        # 'containerapp' not found. If newly added, re-run with --discover
        # No tests selected to run.
        # ----------------------------------------------------------------------
        # For the recommended azdev test example, please refer to: `azdev test --help`
        # `python -m azdev test --no-exitfirst --discover --verbose azext_containerapp`
        test_args = [sys.executable, '-m', 'azdev', 'test', '--no-exitfirst', '--discover', '--verbose', pkg_name]
        logger.warning(f'test_args: {test_args}')

        run_command(test_args, check_return_code=True)
        logger.info(f'uninstalling extension: {ext_name}')
        cmd = ['azdev', 'extension', 'remove', ext_name]
        run_command(cmd, check_return_code=True)


def test_source_wheels():
    # Test we can build all sources into wheels and that metadata from the wheel is valid
    built_whl_dir = tempfile.mkdtemp()
    source_extensions = [os.path.join(SRC_PATH, n) for n in os.listdir(SRC_PATH)
                         if os.path.isdir(os.path.join(SRC_PATH, n))]
    for s in source_extensions:
        # Skip empty dirs left over from removed extensions. Git doesn't track empty dirs, so these
        # only ever show up locally.
        if not any(d.startswith('azext_') and os.path.isfile(os.path.join(s, d, '__init__.py'))
                   for d in os.listdir(s)):
            continue
        # An extension is buildable through either pyproject.toml or a legacy setup.py
        if not any(os.path.isfile(os.path.join(s, f)) for f in ('pyproject.toml', 'setup.py')):
            raise RuntimeError("Extension {} has neither pyproject.toml nor setup.py, "
                               "so no wheel can be built for it.".format(os.path.basename(s)))
        try:
            # Pass the source dir as an argument instead of using cwd. With cwd set to the extension
            # folder, the build/ dir setuptools drops there shadows the `build` module and every run
            # after the first one fails.
            # --no-isolation keeps parity with the old `setup.py bdist_wheel` behaviour, which
            # extensions whose setup.py imports their own azext_* package still depend on.
            # TODO: drop --no-isolation once those imports are gone.
            check_output([sys.executable, '-m', 'build', '--wheel', '--no-isolation',
                          '--outdir', built_whl_dir, s], stderr=STDOUT)
        except CalledProcessError as err:
            raise RuntimeError("Unable to build extension {} :\n{}".format(
                s, err.output.decode('utf-8', 'replace'))) from err
    # Export built wheels so CI can publish them as artifacts
    wheels_out_dir = os.environ.get('WHEELS_OUTPUT_DIR')
    if wheels_out_dir:
        try:
            os.makedirs(wheels_out_dir, exist_ok=True)
            for fname in os.listdir(built_whl_dir):
                src_path = os.path.join(built_whl_dir, fname)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, os.path.join(wheels_out_dir, fname))
            logger.warning(f'Exported wheels to: {wheels_out_dir}')
        except Exception as ex:
            logger.exception(f'Failed to export wheels to {wheels_out_dir}: {ex}')
    shutil.rmtree(built_whl_dir)


if __name__ == '__main__':
    test_extension()
    test_source_wheels()
