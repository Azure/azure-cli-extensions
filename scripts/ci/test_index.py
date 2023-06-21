#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

""" Test the index and the wheels from both the index and from source extensions in repository """

from __future__ import print_function

import glob
import hashlib
import json
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

from packaging import version
from wheel.install import WHEEL_INFO_RE

from util import SRC_PATH
from util import get_ext_metadata, get_whl_from_url, get_index_data, build_extension


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_sha256sum(a_file):
    sha256 = hashlib.sha256()
    with open(a_file, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def check_min_version_from_local_whl(ext_name, whl_file):
    try:
        build_extension(ext_name)
        extensions_dir = tempfile.mkdtemp()
        extract_dir = tempfile.mkdtemp(dir=extensions_dir)
        whl_file = glob.glob(whl_file)[0]
        local_metadata = get_ext_metadata(extract_dir, whl_file, ext_name)
        if 'azext.minCliCoreVersion' not in local_metadata:
            raise AssertionError(f'{ext_name} can not get azext.minCliCoreVersion')
    except Exception as e:
        logger.error(f'{ext_name} can not get azext.minCliCoreVersion: {e}')
        raise e


def get_all_tests():
    all_tests = []
    for src_d in os.listdir(SRC_PATH):
        src_d_full = os.path.join(SRC_PATH, src_d)
        if not os.path.isdir(src_d_full):
            continue
        pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)

        # If running in Travis CI, only run tests for edited extensions
        commit_range = os.environ.get('TRAVIS_COMMIT_RANGE')
        if commit_range and not subprocess.check_output(
                ['git', '--no-pager', 'diff', '--name-only', commit_range, '--', src_d_full]):
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
                cmd = cmd_tpl.format(commit_start=ado_target_branch, commit_end=ado_branch_last_commit,
                                     code_dir=src_d_full)
                if not subprocess.check_output(shlex.split(cmd)):
                    continue

        # Find the package and check it has tests
        # /mnt/vss/_work/1/s/src/healthcareapis/azext_healthcareapis/tests
        test_dir = os.path.isdir(os.path.join(src_d_full, pkg_name, 'tests'))
        if pkg_name and test_dir:
            # [('azext_healthcareapis', '/mnt/vss/_work/1/s/src/healthcareapis')]
            all_tests.append((pkg_name, src_d_full))
    logger.info(f'ado_branch_last_commit: {ado_branch_last_commit}, '
                f'ado_target_branch: {ado_target_branch}, '
                f'detect which extension need to test: {all_tests}.')
    return all_tests


class TestIndex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.longMessage = True
        cls.index = get_index_data()
        cls.whl_cache_dir = tempfile.mkdtemp()
        cls.whl_cache = {}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.whl_cache_dir)

    def test_format_version(self):
        self.assertEqual(self.index['formatVersion'], '1')

    def test_format_extensions_key(self):
        self.assertIn('extensions', self.index)

    def test_format_extensions_value(self):
        self.assertIsInstance(self.index['extensions'], dict)

    def test_extension_filenames(self):
        for ext_name, exts in self.index['extensions'].items():
            self.assertEqual(ext_name.find('_'), -1, "Extension names should not contain underscores. "
                                                     "Found {}".format(ext_name))
            for item in exts:
                self.assertTrue(item['filename'].endswith('.whl'),
                                "Filename {} must end with .whl".format(item['filename']))
                self.assertEqual(ext_name, item['metadata']['name'],
                                 "Extension name mismatch in extensions['{}']. "
                                 "Found an extension in the list with name "
                                 "{}".format(ext_name, item['metadata']['name']))
                parsed_filename = WHEEL_INFO_RE(item['filename'])
                p = parsed_filename.groupdict()
                self.assertTrue(p.get('name'), "Can't get name for {}".format(item['filename']))
                built_wheel = p.get('abi') == 'none' and p.get('plat') == 'any'
                self.assertTrue(built_wheel,
                                "{} of {} not platform independent wheel. "
                                "It should end in -none-any.whl".format(item['filename'], ext_name))

    def test_extension_url_filename(self):
        for exts in self.index['extensions'].values():
            for item in exts:
                self.assertEqual(os.path.basename(item['downloadUrl']), item['filename'],
                                 "Filename must match last segment of downloadUrl")

    def test_extension_url_pypi(self):
        for exts in self.index['extensions'].values():
            for item in exts:
                url = item['downloadUrl']
                pypi_url_prefix = 'https://pypi.python.org/packages/'
                pythonhosted_url_prefix = 'https://files.pythonhosted.org/packages/'
                if url.startswith(pypi_url_prefix):
                    new_url = url.replace(pypi_url_prefix, pythonhosted_url_prefix)
                    hash_pos = new_url.find('#')
                    new_url = new_url if hash_pos == -1 else new_url[:hash_pos]
                    self.fail("Replace {} with {}\n"
                              "See for more info https://wiki.archlinux.org/index.php/Python_package_guidelines"
                              "#PyPI_download_URLs".format(url, new_url))

    def test_filename_duplicates(self):
        filenames = []
        for exts in self.index['extensions'].values():
            for item in exts:
                filenames.append(item['filename'])
        filename_seen = set()
        dups = []
        for f in filenames:
            if f in filename_seen:
                dups.append(f)
            filename_seen.add(f)
        self.assertFalse(dups, "Duplicate filenames found {}".format(dups))

    @unittest.skipUnless(os.getenv('CI'), 'Skipped as not running on CI')
    def test_checksums(self):
        for exts in self.index['extensions'].values():
            # only test the latest version
            item = max(exts, key=lambda ext: version.parse(ext['metadata']['version']))
            ext_file = get_whl_from_url(item['downloadUrl'], item['filename'],
                                        self.whl_cache_dir, self.whl_cache)
            print(ext_file)
            computed_hash = get_sha256sum(ext_file)
            self.assertEqual(computed_hash, item['sha256Digest'],
                             "Computed {} but found {} in index for {}".format(computed_hash,
                                                                               item['sha256Digest'],
                                                                               item['filename']))

    @unittest.skipUnless(os.getenv('CI'), 'Skipped as not running on CI')
    def test_metadata(self):
        skipable_extension_thresholds = {
            'ip-group': '0.1.2',
            'vm-repair': '0.3.1',
            'mixed-reality': '0.0.2',
            'subscription': '0.1.4',
            'managementpartner': '0.1.3',
            'log-analytics': '0.2.1'
        }

        historical_extensions = {
            'keyvault-preview': '0.1.3',
            'log-analytics': '0.2.1'
        }

        extensions_dir = tempfile.mkdtemp()
        for ext_name, exts in self.index['extensions'].items():
            # only test the latest version
            item = max(exts, key=lambda ext: version.parse(ext['metadata']['version']))
            ext_dir = tempfile.mkdtemp(dir=extensions_dir)
            ext_file = get_whl_from_url(item['downloadUrl'], item['filename'],
                                        self.whl_cache_dir, self.whl_cache)

            print(ext_file)

            ext_version = item['metadata']['version']
            try:
                metadata = get_ext_metadata(ext_dir, ext_file, ext_name)    # check file exists
            except ValueError as ex:
                if ext_name in skipable_extension_thresholds:
                    threshold_version = skipable_extension_thresholds[ext_name]

                    if version.parse(ext_version) <= version.parse(threshold_version):
                        continue
                    else:
                        raise ex
                else:
                    raise ex

            try:
                # check key properties exists
                self.assertIn('azext.minCliCoreVersion', metadata)
            except AssertionError as ex:
                if ext_name in historical_extensions:
                    threshold_version = historical_extensions[ext_name]

                    if version.parse(ext_version) <= version.parse(threshold_version):
                        continue
                    else:
                        raise ex
                else:
                    raise ex

            # Due to https://github.com/pypa/wheel/issues/195 we prevent whls built with 0.31.0 or greater.
            # 0.29.0, 0.30.0 are the two previous versions before that release.
            supported_generators = ['bdist_wheel (0.29.0)', 'bdist_wheel (0.30.0)']
            self.assertIn(metadata.get('generator'), supported_generators,
                          "{}: 'generator' should be one of {}. "
                          "Build the extension with a different version of the 'wheel' package "
                          "(e.g. `pip install wheel==0.30.0`). "
                          "This is due to https://github.com/pypa/wheel/issues/195".format(ext_name,
                                                                                           supported_generators))
            self.assertDictEqual(metadata, item['metadata'],
                                 "Metadata for {} in index doesn't match the expected of: \n"
                                 "{}".format(item['filename'], json.dumps(metadata, indent=2, sort_keys=True,
                                                                          separators=(',', ': '))))

        # Find all the modified extensions and check min version from local whl
        all_tests = get_all_tests()
        for pkg_name, pkg_dir in all_tests:
            ext_name = pkg_dir.split('/')[-1]
            local_metadata = check_min_version_from_local_whl(ext_name, os.path.join('.', 'dist', '*.whl'))
            self.assertIn('azext.minCliCoreVersion', local_metadata)
        shutil.rmtree(extensions_dir)


if __name__ == '__main__':
    unittest.main()
