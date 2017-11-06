#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

""" Test the index and the wheels from both the index and from source extensions in repository """

from __future__ import print_function

import os
import json
import tempfile
import unittest
import zipfile
import hashlib
import shutil
import subprocess
from util import get_repo_root
from wheel.install import WHEEL_INFO_RE

INDEX_PATH = os.path.join(get_repo_root(), 'src', 'index.json')
SRC_PATH = os.path.join(get_repo_root(), 'src')

# Extensions to skip dep. check. Aim to keep this list empty.
SKIP_DEP_CHECK = ['azure-cli-iot-ext']


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
    if len(pos_mods) != 1:
        raise AssertionError("Expected 1 module to load starting with "
                             "'{}': got {}".format(EXTENSIONS_MOD_PREFIX, pos_mods))
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
        if parsed_dist_info_dir and parsed_dist_info_dir.groupdict().get('name') == ext_name.replace('-', '_'):
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
                universal_wheel = p.get('pyver') == 'py2.py3' and p.get('abi') == 'none' and p.get('plat') == 'any'
                self.assertTrue(universal_wheel,
                                "{} of {} not universal (platform independent) wheel. "
                                "It should end in py2.py3-none-any.whl".format(item['filename'], ext_name))

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
                run_requires = metadata.get('run_requires')
                if run_requires and ext_name not in SKIP_DEP_CHECK:
                    deps = run_requires[0]['requires']
                    self.assertTrue(all(not dep.startswith('azure-') for dep in deps),
                                    "Dependencies of {} use disallowed extension dependencies. "
                                    "Remove these dependencies: {}".format(item['filename'], deps))
        shutil.rmtree(extensions_dir)


class TestSourceWheels(unittest.TestCase):

    def test_source_wheels(self):
        # Test we can build all sources into wheels and that metadata from the wheel is valid
        from subprocess import PIPE
        built_whl_dir = tempfile.mkdtemp()
        source_extensions = [os.path.join(SRC_PATH, n) for n in os.listdir(SRC_PATH)
                             if os.path.isdir(os.path.join(SRC_PATH, n))]
        for s in source_extensions:
            if not os.path.isfile(os.path.join(s, 'setup.py')):
                continue
            try:
                subprocess.check_call(['python', 'setup.py', 'bdist_wheel', '-q', '-d', built_whl_dir],
                                      cwd=s, stdout=PIPE, stderr=PIPE)
            except subprocess.CalledProcessError as err:
                self.fail("Unable to build extension {} : {}".format(s, err))
        for filename in os.listdir(built_whl_dir):
            ext_file = os.path.join(built_whl_dir, filename)
            ext_dir = tempfile.mkdtemp(dir=built_whl_dir)
            ext_name = WHEEL_INFO_RE(filename).groupdict().get('name')
            metadata = get_ext_metadata(ext_dir, ext_file, ext_name)
            run_requires = metadata.get('run_requires')
            if run_requires and ext_name not in SKIP_DEP_CHECK:
                deps = run_requires[0]['requires']
                self.assertTrue(all(not dep.startswith('azure-') for dep in deps),
                                "Dependencies of {} use disallowed extension dependencies. "
                                "Remove these dependencies: {}".format(filename, deps))
        shutil.rmtree(built_whl_dir)


if __name__ == '__main__':
    unittest.main()
