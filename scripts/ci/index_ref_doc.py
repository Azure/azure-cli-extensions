#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import tempfile
import unittest
import shutil
from subprocess import check_call
from pkg_resources import parse_version, get_distribution

from six import with_metaclass

from util import get_index_data, get_whl_from_url, get_repo_root


REF_GEN_SCRIPT = os.path.join(get_repo_root(), 'scripts', 'refdoc', 'generate.py')

REF_DOC_OUT_DIR = os.environ.get('AZ_EXT_REF_DOC_OUT_DIR', tempfile.mkdtemp())

if not os.path.isdir(REF_DOC_OUT_DIR):
    print('{} is not a directory'.format(REF_DOC_OUT_DIR))
    sys.exit(1)

ALL_TESTS = []

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
    ALL_TESTS.append((extension_name, chosen['downloadUrl'], chosen['filename']))


class TestIndexRefDocsMeta(type):
    def __new__(mcs, name, bases, _dict):

        def gen_test(ext_name, ext_url, filename):
            def test(self):
                ext_file = get_whl_from_url(ext_url, filename, self.whl_dir)
                ref_doc_out_dir = os.path.join(REF_DOC_OUT_DIR, ext_name)
                if not os.path.isdir(ref_doc_out_dir):
                    os.mkdir(ref_doc_out_dir)
                script_args = [sys.executable, REF_GEN_SCRIPT, '--extension-file', ext_file, '--output-dir',
                               ref_doc_out_dir]
                check_call(script_args)
            return test

        for ext_name, ext_url, filename in ALL_TESTS:
            test_name = "test_ref_doc_%s" % ext_name
            _dict[test_name] = gen_test(ext_name, ext_url, filename)
        return type.__new__(mcs, name, bases, _dict)


class IndexRefDocs(with_metaclass(TestIndexRefDocsMeta, unittest.TestCase)):

    def setUp(self):
        self.whl_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.whl_dir)


if __name__ == '__main__':
    unittest.main()
