#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

""" Test the index and the wheels from both the index and from source extensions in repository """

from __future__ import print_function

import os
import re
import tempfile
import unittest
import hashlib
import shutil

from distutils.version import LooseVersion

from util import get_ext_metadata, get_whl_from_url, get_index_data, verify_dependency


WHEEL_INFO_RE = re.compile(
    r"""^(?P<namever>(?P<name>.+?)-(?P<ver>\d.*?))(-(?P<build>\d.*?))?
     -(?P<pyver>[a-z].+?)-(?P<abi>.+?)-(?P<plat>.+?)(\.whl|\.dist-info)$""",
    re.VERBOSE).match


def get_sha256sum(a_file):
    sha256 = hashlib.sha256()
    with open(a_file, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest()


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
            for item in exts:
                ext_file = get_whl_from_url(item['downloadUrl'], item['filename'],
                                            self.whl_cache_dir, self.whl_cache)
                computed_hash = get_sha256sum(ext_file)
                self.assertEqual(computed_hash, item['sha256Digest'],
                                 "Computed {} but found {} in index for {}".format(computed_hash,
                                                                                   item['sha256Digest'],
                                                                                   item['filename']))

    # @unittest.skipUnless(os.getenv('CI'), 'Skipped as not running on CI')
    def test_metadata(self):
        skipable_extension_thresholds = {
            'ip-group': '0.1.2',
            'vm-repair': '0.3.1',
            'mixed-reality': '0.0.2',
            'subscription': '0.1.4',
            'managementpartner': '0.1.3',
            'log-analytics': '0.2.1'
        }

        historical_extensios = {
            'keyvault-preview': '0.1.3',
            'log-analytics': '0.2.1'
        }

        extensions_dir = tempfile.mkdtemp()
        for ext_name, exts in self.index['extensions'].items():
            for item in exts:
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

                        if LooseVersion(ext_version) <= LooseVersion(threshold_version):
                            continue
                        else:
                            raise ex
                    else:
                        raise ex

                try:
                    self.assertIn('azext.minCliCoreVersion', metadata)  # check key properties exists
                except AssertionError as ex:
                    if ext_name in historical_extensios:
                        threshold_version = historical_extensios[ext_name]

                        if LooseVersion(ext_version) <= LooseVersion(threshold_version):
                            continue
                        else:
                            raise ex
                    else:
                        raise ex

                wheel_metadata = get_ext_metadata(ext_dir, ext_file)
                index_metadata = item['metadata']

                # compatible way compare metadata between wheel file and index.json
                self.assertEqual(index_metadata['name'], wheel_metadata['name'])
                self.assertEqual(index_metadata['version'], wheel_metadata['version'])
                self.assertEqual(index_metadata['license'], wheel_metadata['license'])
                self.assertEqual(index_metadata['summary'], wheel_metadata['summary'])

                if index_metadata.get('classifiers') and wheel_metadata.get('classifiers'):
                    self.assertEqual(index_metadata['classifiers'], wheel_metadata['classifiers'])

                if index_metadata.get('run_requires') and wheel_metadata.get('requires_dist'):
                    self.assertEqual(index_metadata['run_requires'][0]['requires'], wheel_metadata['requires_dist'])
                if index_metadata.get('requires_dist') and wheel_metadata.get('requires_dist'):
                    self.assertEqual(index_metadata['requires_dist'], wheel_metadata['requires_dist'])

                if index_metadata.get('extensions') is not None:
                    python_details = index_metadata['extensions']['python.details']
                    self.assertEqual(python_details['project_urls']['Home'], wheel_metadata['home_page'])
                    self.assertEqual(python_details['contacts'][0]['name'], wheel_metadata['author'])
                    self.assertEqual(python_details['contacts'][0]['email'], wheel_metadata['author_email'])
                else:
                    self.assertEqual(index_metadata['author'], wheel_metadata['author'])
                    self.assertEqual(index_metadata['home_page'], wheel_metadata['home_page'])
                    self.assertEqual(index_metadata['platforms'], wheel_metadata['platforms'])
                    self.assertEqual(index_metadata['author_email'], wheel_metadata['author_email'])

        shutil.rmtree(extensions_dir)


if __name__ == '__main__':
    unittest.main()
