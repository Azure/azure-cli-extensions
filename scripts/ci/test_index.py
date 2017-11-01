# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import json
import tempfile
import unittest
import hashlib
import shutil
from util import get_repo_root
from wheel.install import WHEEL_INFO_RE

INDEX_PATH = os.path.join(get_repo_root(), 'src', 'index.json')


def catch_dup_keys(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError("duplicate key {}".format(k))
        seen[k] = v
    return seen


def get_index_data():
    try:
        with open(INDEX_PATH) as f:
            return json.load(f, object_pairs_hook=catch_dup_keys)
    except ValueError as err:
        raise AssertionError("Invalid JSON in {}: {}".format(INDEX_PATH, err))


def get_whl_from_url(url, filename, tmp_dir, whl_cache):
    if url in whl_cache:
        return whl_cache[url]
    import requests
    r = requests.get(url, stream=True)
    assert r.status_code == 200, "Request to {} failed with {}".format(url, r.status_code)
    ext_file = os.path.join(tmp_dir, filename)
    with open(ext_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # ignore keep-alive new chunks
                f.write(chunk)
    whl_cache[url] = ext_file
    return ext_file


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
            for item in exts:
                self.assertTrue(item['filename'].endswith('.whl'),
                                "Filename {} must end with .whl".format(item['filename']))
                self.assertTrue(item['filename'].startswith(ext_name),
                                "Filename {} must start with {}".format(item['filename'], ext_name))
                parsed_filename = WHEEL_INFO_RE(item['filename'])
                p = parsed_filename.groupdict()
                universal_wheel = p.get('name') and p.get('pyver') == 'py2.py3' and p.get('abi') == 'none' \
                                  and p.get('plat') == 'any'
                self.assertTrue(universal_wheel,
                                "{} of {} not universal (platform independent) wheel. "
                                "It should end in py2.py3-none-any.whl".format(item['filename'], ext_name))

    def test_extension_url_filename(self):
        for exts in self.index['extensions'].values():
            for item in exts:
                self.assertEqual(os.path.basename(item['downloadUrl']), item['filename'],
                                 "Filename must match last segment of downloadUrl")

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
    # def test_metadata(self):
    #     tmp_dir = tempfile.mkdtemp()
    #     for exts in self.index['extensions'].values():
    #         for item in exts:
    #             ext_file = get_whl_from_url(item['downloadUrl'], item['filename'],
    #                                         self.whl_cache_dir, self.whl_cache)


if __name__ == '__main__':
    unittest.main()
