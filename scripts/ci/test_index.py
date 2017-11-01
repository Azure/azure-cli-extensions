# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
import json
import tempfile
import unittest
import zipfile
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


def get_extension_modname(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L153
    EXTENSIONS_MOD_PREFIX = 'azext_'
    pos_mods = [n for n in os.listdir(ext_dir)
                if n.startswith(EXTENSIONS_MOD_PREFIX) and os.path.isdir(os.path.join(ext_dir, n))]
    return pos_mods[0]


def get_azext_metadata(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L109
    AZEXT_METADATA_FILENAME = 'azext_metadata.json'
    azext_metadata = None
    ext_modname = get_extension_modname(ext_dir=ext_dir)
    azext_metadata_filepath = os.path.join(ext_dir, ext_modname, AZEXT_METADATA_FILENAME)
    if os.path.isfile(azext_metadata_filepath):
        with open(azext_metadata_filepath) as f:
            azext_metadata = json.load(f)
    return azext_metadata


def get_ext_metadata(ext_dir, ext_file, ext_name):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L89
    WHL_METADATA_FILENAME = 'metadata.json'
    zip_ref = zipfile.ZipFile(ext_file, 'r')
    zip_ref.extractall(ext_dir)
    zip_ref.close()
    metadata = {}
    dist_info_dirs = [f for f in os.listdir(ext_dir) if f.endswith('.dist-info')]
    azext_metadata = get_azext_metadata(ext_dir)
    if azext_metadata:
        metadata.update(azext_metadata)
    for dist_info_dirname in dist_info_dirs:
        parsed_dist_info_dir = WHEEL_INFO_RE(dist_info_dirname)
        if parsed_dist_info_dir and parsed_dist_info_dir.groupdict().get('name') == ext_name:
            whl_metadata_filepath = os.path.join(ext_dir, dist_info_dirname, WHL_METADATA_FILENAME)
            if os.path.isfile(whl_metadata_filepath):
                with open(whl_metadata_filepath) as f:
                    metadata.update(json.load(f))
    return metadata


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
                self.assertTrue(p.get('name'), "Can't get name for {}".format(item['filename']))
                universal_wheel = p.get('pyver') == 'py2.py3' and p.get('abi') == 'none' and p.get('plat') == 'any'
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

    @unittest.skipUnless(os.getenv('CI'), 'Skipped as not running on CI')
    def test_metadata(self):
        self.maxDiff = None
        extensions_dir = tempfile.mkdtemp()
        for ext_name, exts in self.index['extensions'].items():
            for item in exts:
                ext_dir = tempfile.mkdtemp(dir=extensions_dir)
                ext_file = get_whl_from_url(item['downloadUrl'], item['filename'],
                                            self.whl_cache_dir, self.whl_cache)
                metadata = get_ext_metadata(ext_dir, ext_file, ext_name)
                self.assertDictEqual(metadata, item['metadata'],
                                     "Metadata for {} in index doesn't match the expected of: \n"
                                     "{}".format(item['filename'], json.dumps(metadata, indent=2, sort_keys=True,
                                                                              separators=(',', ': '))))
        shutil.rmtree(extensions_dir)


if __name__ == '__main__':
    unittest.main()
