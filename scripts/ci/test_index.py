#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

""" Test the index and the wheels from both the index and from source extensions in repository """

from __future__ import print_function

import copy
import glob
import hashlib
import json
import logging
import os
import shutil
import tempfile
import unittest

from packaging import version
from util import SRC_PATH
from util import get_ext_metadata, get_whl_from_url, get_index_data


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


# Cosmetic packaging-format fields that the legacy wheel==0.30.0 metadata path
# emitted but that carry no extension behaviour (they describe the *build tool*
# and METADATA serialization, not the extension). The pkginfo-based path no
# longer reproduces them, so they are ignored when comparing generated metadata
# against the published index. Kept in sync with the tests/e2e/packaging
# metadata parity allowlist.
_METADATA_NOISE_TOP_LEVEL = ('generator', 'metadata_version', 'test_requires', 'license_file')


def _canonical_requirement(raw):
    """Reduce a requirement string to its semantic identity.

    ``run_requires`` in the published index is serialized inconsistently across
    the years of tooling that produced it: a dependency may appear as
    ``"jinja2 (~=2.10)"`` (PEP 314 form), ``"jinja2~=2.10"`` (PEP 508 form), or
    both (wheel==0.30.0 emitted each requirement twice). These are all the *same*
    dependency. Canonicalize to ``name + specifier (+ marker)`` so that only a
    genuine dependency change (added/removed package, different version pin) is
    treated as a difference -- spelling, parentheses and ordering are not.
    """
    text = raw.replace('(', '').replace(')', '').strip()
    try:
        from packaging.requirements import Requirement
        req = Requirement(text)
        extras = ''.join(sorted('[{}]'.format(e) for e in req.extras))
        marker = ' ; {}'.format(req.marker) if req.marker else ''
        return '{}{}{}{}'.format(req.name.lower(), extras, str(req.specifier), marker)
    except Exception:  # pragma: no cover - non-PEP-508 string, compare verbatim
        return raw.strip()


def _canonical_run_requires(run_requires):
    """Flatten ``run_requires`` to a sorted set of canonical requirements.

    Each entry may carry an ``environment``/``extra`` condition; preserve it so
    a conditional dependency is not conflated with an unconditional one.
    """
    canon = set()
    for entry in run_requires or []:
        if not isinstance(entry, dict):
            continue
        condition = entry.get('environment') or entry.get('extra') or ''
        for raw in entry.get('requires') or []:
            req = _canonical_requirement(raw)
            canon.add('{} ; {}'.format(req, condition) if condition else req)
    return sorted(canon)


def _without_metadata_noise(metadata):
    cleaned = copy.deepcopy(metadata)
    for key in _METADATA_NOISE_TOP_LEVEL:
        cleaned.pop(key, None)
    # The pkginfo path emits empty lists for extras/run_requires where the
    # legacy wheel==0.30.0 path omitted them entirely. Treat an empty value as
    # equivalent to "absent" so a no-dependency extension matches either form.
    for key in ('extras', 'run_requires'):
        if not cleaned.get(key):
            cleaned.pop(key, None)
    extras = cleaned.get('extras')
    if isinstance(extras, list):
        cleaned['extras'] = sorted(extras)
    # Compare dependencies by their semantic identity, not their (historically
    # inconsistent) string serialization. A real dependency change still fails.
    if isinstance(cleaned.get('run_requires'), list):
        cleaned['run_requires'] = _canonical_run_requires(cleaned['run_requires'])
    details = cleaned.get('extensions', {}).get('python.details')
    if isinstance(details, dict):
        details.pop('document_names', None)
    return cleaned


def check_min_version(extension_name, metadata):
    if 'azext.minCliCoreVersion' not in metadata:
        try:
            azext_metadata = glob.glob(os.path.join(SRC_PATH, extension_name, 'azext_*', 'azext_metadata.json'))[0]
            with open(azext_metadata, 'r') as f:
                metadata = json.load(f)
                if not metadata.get('azext.minCliCoreVersion'):
                    raise AssertionError(f'{extension_name} can not get azext.minCliCoreVersion')
        except Exception as e:
            logger.error(f'{extension_name} can not get azext.minCliCoreVersion: {e}')
            raise e


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
                # Extensions must be published as platform-independent wheels,
                # i.e. the filename ends in ``-none-any.whl`` (ABI tag ``none``,
                # platform tag ``any``). This was previously derived from
                # ``wheel.install.WHEEL_INFO_RE``; it is asserted directly here
                # so the check no longer depends on the ``wheel`` package.
                self.assertTrue(item['filename'].endswith('-none-any.whl'),
                                "{} of {} is not a platform-independent wheel. "
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
                check_min_version(ext_name, metadata)
            except AssertionError as ex:
                if ext_name in historical_extensions:
                    threshold_version = historical_extensions[ext_name]

                    if version.parse(ext_version) <= version.parse(threshold_version):
                        continue
                    else:
                        raise ex
                else:
                    raise ex

            # The pkginfo-based metadata path intentionally omits
            # wheel==0.30.0-specific fields (e.g. `generator`, `document_names`).
            # Ignore those known, benign differences and compare the rest.
            self.assertDictEqual(_without_metadata_noise(metadata),
                                 _without_metadata_noise(item['metadata']),
                                 "Metadata for {} in index doesn't match the expected of: \n"
                                 "{}".format(item['filename'], json.dumps(metadata, indent=2, sort_keys=True,
                                                                          separators=(',', ': '))))

        shutil.rmtree(extensions_dir)


if __name__ == '__main__':
    unittest.main()
