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
from subprocess import check_output, check_call, CalledProcessError

import mock
from wheel.install import WHEEL_INFO_RE
from six import with_metaclass

from util import get_ext_metadata, verify_dependency, SRC_PATH


ALL_TESTS = []

for src_d in os.listdir(SRC_PATH):
    src_d_full = os.path.join(SRC_PATH, src_d)
    if os.path.isdir(src_d_full):
        pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)
        # Find the package and check it has tests
        if pkg_name and os.path.isdir(os.path.join(src_d_full, pkg_name, 'tests')):
            ALL_TESTS.append((pkg_name, src_d_full))


class TestExtensionSourceMeta(type):
    def __new__(mcs, name, bases, _dict):

        def gen_test(ext_path):
            def test(self):
                ext_install_dir = os.path.join(self.ext_dir, 'ext')
                pip_args = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--target',
                            ext_install_dir, ext_path]
                check_call(pip_args)
                unittest_args = [sys.executable, '-m', 'unittest', 'discover', '-v', ext_path]
                env = os.environ.copy()
                env['PYTHONPATH'] = ext_install_dir
                check_call(unittest_args, env=env)
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


class TestSourceWheels(unittest.TestCase):

    def test_source_wheels(self):
        # Test we can build all sources into wheels and that metadata from the wheel is valid
        built_whl_dir = tempfile.mkdtemp()
        source_extensions = [os.path.join(SRC_PATH, n) for n in os.listdir(SRC_PATH)
                             if os.path.isdir(os.path.join(SRC_PATH, n))]
        for s in source_extensions:
            if not os.path.isfile(os.path.join(s, 'setup.py')):
                continue
            try:
                check_output(['python', 'setup.py', 'bdist_wheel', '-q', '-d', built_whl_dir], cwd=s)
            except CalledProcessError as err:
                self.fail("Unable to build extension {} : {}".format(s, err))
        for filename in os.listdir(built_whl_dir):
            ext_file = os.path.join(built_whl_dir, filename)
            ext_dir = tempfile.mkdtemp(dir=built_whl_dir)
            ext_name = WHEEL_INFO_RE(filename).groupdict().get('name')
            metadata = get_ext_metadata(ext_dir, ext_file, ext_name)
            run_requires = metadata.get('run_requires')
            if run_requires:
                deps = run_requires[0]['requires']
                self.assertTrue(all(verify_dependency(dep) for dep in deps),
                                "Dependencies of {} use disallowed extension dependencies. "
                                "Remove these dependencies: {}".format(filename, deps))
        shutil.rmtree(built_whl_dir)


if __name__ == '__main__':
    unittest.main()
