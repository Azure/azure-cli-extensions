#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import logging
import os
import subprocess
import sys

from util import diff_code

from azdev.utilities.path import get_cli_repo_path, get_ext_repo_paths
from subprocess import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

pull_request_number = os.environ.get('PULL_REQUEST_NUMBER', None)
job_name = os.environ.get('JOB_NAME', None)
azdev_test_result_dir = os.path.expanduser("~/.azdev/env_config/mnt/vss/_work/1/s/env")
src_branch = os.environ.get('PR_TARGET_BRANCH', None)
target_branch = 'merged_pr'
base_meta_path = '~/_work/1/base_meta'
diff_meta_path = '~/_work/1/diff_meta'
output_path = '~/_work/1/output_meta'


def install_extensions(diif_ref, branch):
    for tname, ext_path in diif_ref:
        ext_name = ext_path.split('/')[-1]
        logger.info(f'installing extension: {ext_name}')
        cmd = ['azdev', 'extension', 'add', ext_name]
        logger.info(f'cmd: {cmd}')
        out = run(cmd, capture_output=True, text=True)
        if out.returncode and branch == 'base' and 'ERROR: extension(s) not found' in out.stderr:
            print(f"{cmd} failed, extesion {ext_name} is not exist on base branch, skip it.")
            sys.exit(0)
        elif out.returncode:
            raise RuntimeError(f"{cmd} failed")


def uninstall_extensions(diif_ref):
    for tname, ext_path in diif_ref:
        ext_name = ext_path.split('/')[-1]
        logger.info(f'uninstalling extension: {ext_name}')
        cmd = ['azdev', 'extension', 'remove', ext_name]
        logger.info(f'cmd: {cmd}')
        out = run(cmd)
        if out.returncode:
            raise RuntimeError(f"{cmd} failed")


# def get_diff_meta_files(diff_ref):
#     cmd = ['git', 'checkout', '-b', target_branch]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['git', 'checkout', src_branch]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['git', 'checkout', target_branch]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['git', 'rev-parse', 'HEAD']
#     print(cmd)
#     subprocess.run(cmd)
#     install_extensions(diff_ref, branch='target')
#     cmd = ['azdev', 'command-change', 'meta-export', '--src', src_branch, '--tgt', target_branch, '--repo', get_ext_repo_paths()[0], '--meta-output-path', diff_meta_path]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['ls', '-al', diff_meta_path]
#     print(cmd)
#     subprocess.run(cmd)
#     uninstall_extensions(diff_ref)
#
#
# def get_base_meta_files(diff_ref):
#     cmd = ['git', 'checkout', src_branch]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['git', 'rev-parse', 'HEAD']
#     print(cmd)
#     subprocess.run(cmd)
#     install_extensions(diff_ref, branch='base')
#     cmd = ['azdev', 'command-change', 'meta-export', 'EXT', '--meta-output-path', base_meta_path]
#     print(cmd)
#     subprocess.run(cmd)
#     cmd = ['ls', '-al', base_meta_path]
#     print(cmd)
#     subprocess.run(cmd)


def meta_diff():
    if os.path.exists(diff_meta_path):
        for file in os.listdir(diff_meta_path):
            if file.endswith('.json'):
                cmd = ['azdev', 'command-change', 'meta-diff', '--base-meta-file', os.path.join(base_meta_path, file), '--diff-meta-file', os.path.join(diff_meta_path, file), '--output-file', os.path.join(output_path, file)]
                print(cmd)
                subprocess.run(cmd)
        cmd = ['ls', '-al', output_path]
        print(cmd)
        subprocess.run(cmd)


def azdev_style_check(repo_path, src, tgt):
    for tname, ext_path in diif_ref:
        ext_name = ext_path.split('/')[-1]
        logger.info(f'installing extension: {ext_name}')
        cmd = ['azdev', 'extension', 'add', ext_name]
        logger.info(f'cmd: {cmd}')
        out = run(cmd, capture_output=True, text=True)
        if out.returncode and branch == 'base' and 'ERROR: extension(s) not found' in out.stderr:
            print(f"{cmd} failed, extesion {ext_name} is not exist on base branch, skip it.")
            sys.exit(0)
        elif out.returncode:
            raise RuntimeError(f"{cmd} failed")


def main():
    if pull_request_number != '$(System.PullRequest.PullRequestNumber)':
        logger.info("Start azdev style test ...\n")
        diff_ref = diff_code(src_branch, 'HEAD')
        install_extensions(diff_ref)
        azdev_style_check()


if __name__ == '__main__':
    main()
