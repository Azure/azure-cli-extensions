# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from six import StringIO

from knack import CLI

from azure.cli.core._config import GLOBAL_CONFIG_DIR, ENV_VAR_PREFIX
from azure.cli.core.cloud import get_active_cloud
from azure.cli.core.profiles import get_sdk, supported_api_version, register_resource_type
from azure.cli.testsdk import api_version_constraint
from ..._validators import (get_datetime_type, ipv4_range_type, validate_encryption_source,
                            validate_encryption_services)
from ...profiles import CUSTOM_DATA_STORAGE, CUSTOM_MGMT_PREVIEW_STORAGE


class MockCLI(CLI):
    def __init__(self):
        super(MockCLI, self).__init__(cli_name='mock_cli', config_dir=GLOBAL_CONFIG_DIR,
                                      config_env_var_prefix=ENV_VAR_PREFIX, commands_loader_cls=MockLoader)
        self.cloud = get_active_cloud(self)


class MockLoader(object):
    def __init__(self, ctx):
        self.ctx = ctx
        register_resource_type('latest', CUSTOM_DATA_STORAGE, '2018-03-28')

    def get_models(self, *attr_args, **_):
        from azure.cli.core.profiles import get_sdk
        return get_sdk(self.ctx, CUSTOM_DATA_STORAGE, *attr_args, mod='models')


class MockCmd(object):
    def __init__(self, ctx):
        self.cli_ctx = ctx
        self.loader = MockLoader(self.cli_ctx)

    def get_models(self, *attr_args, **kwargs):
        return get_sdk(self.cli_ctx, CUSTOM_DATA_STORAGE, *attr_args, **kwargs)


class TestStorageValidators(unittest.TestCase):
    def setUp(self):
        self.io = StringIO()
        self.cli = MockCLI()
        self.loader = MockLoader(self.cli)

    def tearDown(self):
        self.io.close()

    def test_datetime_string_type(self):
        input = "2017-01-01T12:30Z"
        actual = get_datetime_type(True)(input)
        expected = "2017-01-01T12:30Z"
        self.assertEqual(actual, expected)

        input = "2017-01-01 12:30"
        with self.assertRaises(ValueError):
            get_datetime_type(True)(input)

    def test_datetime_type(self):
        import datetime
        input = "2017-01-01T12:30Z"
        actual = get_datetime_type(False)(input)
        expected = datetime.datetime(2017, 1, 1, 12, 30, 0)
        self.assertEqual(actual, expected)

        input = "2017-01-01 12:30"
        with self.assertRaises(ValueError):
            actual = get_datetime_type(False)(input)

    def test_ipv4_range_type(self):
        input = "111.22.3.111"
        actual = ipv4_range_type(input)
        expected = input
        self.assertEqual(actual, expected)

        input = "111.22.3.111-222.11.44.111"
        actual = ipv4_range_type(input)
        expected = input
        self.assertEqual(actual, expected)

        input = "111.22"
        with self.assertRaises(ValueError):
            actual = ipv4_range_type(input)

        input = "111.22.33.44-"
        with self.assertRaises(ValueError):
            actual = ipv4_range_type(input)


@api_version_constraint(resource_type=CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class TestEncryptionValidators(unittest.TestCase):
    def setUp(self):
        self.cli = MockCLI()

    def test_validate_encryption_services(self):
        ns = Namespace(encryption_services=['blob'], _cmd=MockCmd(self.cli))
        validate_encryption_services(MockCmd(self.cli), ns)
        self.assertIsNotNone(ns.encryption_services.blob)
        self.assertTrue(ns.encryption_services.blob.enabled)
        self.assertIsNone(ns.encryption_services.file)

        ns = Namespace(encryption_services=['file'], _cmd=MockCmd(self.cli))
        validate_encryption_services(MockCmd(self.cli), ns)
        self.assertIsNotNone(ns.encryption_services.file)
        self.assertTrue(ns.encryption_services.file.enabled)
        self.assertIsNone(ns.encryption_services.blob)

        ns = Namespace(encryption_services=['blob', 'file'], _cmd=MockCmd(self.cli))
        validate_encryption_services(MockCmd(self.cli), ns)
        self.assertIsNotNone(ns.encryption_services.blob)
        self.assertTrue(ns.encryption_services.blob.enabled)
        self.assertIsNotNone(ns.encryption_services.file)
        self.assertTrue(ns.encryption_services.file.enabled)

    def test_validate_encryption_source(self):
        with self.assertRaises(ValueError):
            validate_encryption_source(MockCmd(self.cli),
                                       Namespace(encryption_key_source='Microsoft.Keyvault', _cmd=MockCmd(self.cli)))

        with self.assertRaises(ValueError):
            validate_encryption_source(
                MockCmd(self.cli),
                Namespace(encryption_key_source='Microsoft.Storage', encryption_key_name='key_name',
                          encryption_key_version='key_version', encryption_key_vault='https://example.com/key_uri'))

        ns = Namespace(encryption_key_source='Microsoft.Keyvault', encryption_key_name='key_name',
                       encryption_key_version='key_version', encryption_key_vault='https://example.com/key_uri')
        validate_encryption_source(MockCmd(self.cli), ns)
        self.assertFalse(hasattr(ns, 'encryption_key_name'))
        self.assertFalse(hasattr(ns, 'encryption_key_version'))
        self.assertFalse(hasattr(ns, 'encryption_key_uri'))

        properties = ns.encryption_key_vault_properties
        self.assertEqual(properties.key_name, 'key_name')
        self.assertEqual(properties.key_version, 'key_version')
        self.assertEqual(properties.key_vault_uri, 'https://example.com/key_uri')


if __name__ == '__main__':
    unittest.main()
