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

import mock
from six import with_metaclass

from util import get_repo_root


SOURCES = os.path.join(get_repo_root(), 'src')

ALL_TESTS = []

for src_d in os.listdir(SOURCES):
    src_d_full = os.path.join(SOURCES, src_d)
    if os.path.isdir(src_d_full):
        pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)
        # Find the package and check it has tests
        if pkg_name and os.path.isdir(os.path.join(src_d_full, pkg_name, 'tests')):
            ALL_TESTS.append((pkg_name, src_d_full))


class TestExtensionSourceMeta(type):
    def __new__(mcs, name, bases, _dict):

        def gen_test(ext_path):
            def test(self):
                pip_args = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--target',
                            os.path.join(self.ext_dir, 'ext'), ext_path]
                check_call(pip_args)
                unittest_args = [sys.executable, '-m', 'unittest', 'discover', '-v', ext_path]
                check_call(unittest_args)
            return test

        for tname, ext_path in ALL_TESTS:
            test_name = "test_%s" % tname
            _dict[test_name] = gen_test(ext_path)
        return type.__new__(mcs, name, bases, _dict)


class TestExtensionSource(with_metaclass(TestExtensionSourceMeta, unittest.TestCase)):

    def setUp(self):
        self.ext_dir = tempfile.mkdtemp()
        self.mock_env = mock.patch.dict(os.environ, {'AZURE_EXTENSION_DIR': self.ext_dir})
        self.mock_env.start()

    def tearDown(self):
        self.mock_env.stop()
        shutil.rmtree(self.ext_dir)


if __name__ == '__main__':
    unittest.main()
