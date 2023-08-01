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
import traceback
import unittest
import shutil
import shlex
from subprocess import check_call, check_output, CalledProcessError
from pkg_resources import parse_version, get_distribution

from six import with_metaclass

from util import get_index_data, get_whl_from_url, get_repo_root, SRC_PATH

logger = logging.getLogger(__name__)

REF_GEN_SCRIPT = os.path.join(get_repo_root(), 'scripts', 'refdoc', 'generate.py')

REF_DOC_OUT_DIR = os.environ.get('AZ_EXT_REF_DOC_OUT_DIR', tempfile.mkdtemp())

if not os.path.isdir(REF_DOC_OUT_DIR):
    print('{} is not a directory'.format(REF_DOC_OUT_DIR))
    sys.exit(1)

ALL_TESTS = []
MODIFIED_EXTS = []

for src_d in os.listdir(SRC_PATH):
    src_d_full = os.path.join(SRC_PATH, src_d)
    if not os.path.isdir(src_d_full):
        continue
    pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)

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

    if pkg_name:
        MODIFIED_EXTS.append(src_d)

CLI_VERSION = get_distribution('azure-cli').version

for extension_name, exts in get_index_data()['extensions'].items():
    parsed_cli_version = parse_version(CLI_VERSION)
    filtered_exts = []
    for ext in exts:
        if parsed_cli_version <= parse_version(ext['metadata'].get('azext.maxCliCoreVersion', CLI_VERSION)):
            filtered_exts.append(ext)
    if not filtered_exts:
        continue

    candidates_sorted = sorted(filtered_exts, key=lambda c: parse_version(c['metadata']['version']), reverse=True)
    chosen = candidates_sorted[0]
    if extension_name in MODIFIED_EXTS:
        ALL_TESTS.append((extension_name, chosen['downloadUrl'], chosen['filename']))

logger.warning(f'ado_branch_last_commit: {ado_branch_last_commit}, '
               f'ado_target_branch: {ado_target_branch}, '
               f'MODIFIED_EXTS: {MODIFIED_EXTS}, '
               f'ALL_TESTS: {ALL_TESTS}')


class TestIndexRefDocsMeta(type):
    def __new__(mcs, name, bases, _dict):

        def gen_test(ext_name, ext_url, filename, dep_url):
            def test(self):
                if dep_url.get(ext_name):
                    dep_file = get_whl_from_url(dep_url[ext_name][0], dep_url[ext_name][1], self.whl_dir)
                else:
                    dep_file = None
                ext_file = get_whl_from_url(ext_url, filename, self.whl_dir)
                ref_doc_out_dir = os.path.join(REF_DOC_OUT_DIR, ext_name)
                if not os.path.isdir(ref_doc_out_dir):
                    os.mkdir(ref_doc_out_dir)
                script_args = [sys.executable, REF_GEN_SCRIPT, '--extension-file', ext_file, '--output-dir',
                               ref_doc_out_dir]
                if dep_file:
                    script_args.extend(['--dependent-file', dep_file])
                try:
                    check_call(script_args)
                except CalledProcessError as e:
                    traceback.print_exc()
                    raise e
            return test

        dep_url = {}
        for ext_name, ext_url, filename in ALL_TESTS:
            test_name = "test_ref_doc_%s" % ext_name
            # The containerapp-preview extension is a special case,
            # it must depend on the continerapp extension and cannot run independently.
            if ext_name == 'containerapp':
                dep_url['containerapp-preview'] = [ext_url, filename]
            _dict[test_name] = gen_test(ext_name, ext_url, filename, dep_url)
        return type.__new__(mcs, name, bases, _dict)


class IndexRefDocs(with_metaclass(TestIndexRefDocsMeta, unittest.TestCase)):

    def setUp(self):
        self.whl_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.whl_dir)


if __name__ == '__main__':
    unittest.main()
