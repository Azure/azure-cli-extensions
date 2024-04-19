# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import os
from .common.test_utils import get_test_cmd
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
from ..._utils import _get_sku_name
from ...custom import (certificate_add, certificate_update)
try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

from knack.log import get_logger

logger = get_logger(__name__)
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class BasicTest(unittest.TestCase):
    def _get_basic_mock_client(self, sku='Standard'):
        client = mock.MagicMock()
        client.services.get.return_value = models.ServiceResource(
            sku=models.Sku(
                tier=sku,
                name=_get_sku_name(sku)
            )
        )
        return client


class CertificateTests(BasicTest):

    def test_create_certificate(self):
        client = self._get_basic_mock_client()
        certificate_add(get_test_cmd(), client, 'rg', 'asc', 'my-cert',
                        False, "vault-uri", "kv-cert-name")
        args = client.certificates.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(4, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'my-cert'), args[0][0][0:3])
        resource = args[0][0][3]
        self.assertEqual('vault-uri', resource.properties.vault_uri)
        self.assertEqual('kv-cert-name', resource.properties.key_vault_cert_name)

    def test_update_certificate(self):
        client = self._get_basic_mock_client()
        client.certificates.get.return_value = models.CertificateResource(
            properties=models.KeyVaultCertificateProperties(
                type="KeyVaultCertificate",
                vault_uri="vault-uri",
                key_vault_cert_name="kv-cert-name",
                exclude_private_key=False,
                auto_sync="Disabled")
        )
        certificate_update(get_test_cmd(), client, 'rg', 'asc', 'my-cert', True)
        args = client.certificates.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(4, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'my-cert'), args[0][0][0:3])
        resource = args[0][0][3]
        self.assertEqual("Enabled", resource.properties.auto_sync)
