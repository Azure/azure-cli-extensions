# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_containerapp.containerapp_env_decorator import ContainerappEnvPreviewUpdateDecorator


class TestContainerappEnvUpdateDecorator(unittest.TestCase):

    def _update_payload(self, **overrides):
        parameters = {
            "resource_group_name": "resource-group",
            "name": "environment",
            "hostname": "new.example.com",
        }
        parameters.update(overrides)
        client = mock.MagicMock()
        client.show.return_value = {"location": "eastus", "properties": {}}
        decorator = ContainerappEnvPreviewUpdateDecorator(
            cmd=mock.MagicMock(), client=client, raw_parameters=parameters, models="models")
        decorator.validate_arguments()
        decorator.construct_payload()
        decorator.update()
        return client.update.call_args.kwargs["managed_environment_envelope"].get("properties", {})

    def test_updates_dns_suffix_without_replacing_certificate(self):
        properties = self._update_payload()
        self.assertEqual({"dnsSuffix": "new.example.com"}, properties.get("customDomainConfiguration", {}))

    @mock.patch("azext_containerapp.containerapp_env_decorator.load_cert_file",
                return_value=("certificate-data", None))
    def test_updates_dns_suffix_with_file_certificate(self, _):
        properties = self._update_payload(certificate_file="certificate.pfx", certificate_password="password")
        self.assertEqual({
            "dnsSuffix": "new.example.com",
            "certificateValue": "certificate-data",
            "certificatePassword": "password",
            "certificateKeyVaultProperties": None,
        }, properties.get("customDomainConfiguration", {}))

    def test_updates_dns_suffix_with_key_vault_certificate(self):
        properties = self._update_payload(certificate_key_vault_url="https://vault.vault.azure.net/secrets/certificate")
        self.assertEqual({
            "dnsSuffix": "new.example.com",
            "certificateKeyVaultProperties": {
                "identity": "system",
                "keyVaultUrl": "https://vault.vault.azure.net/secrets/certificate",
            },
            "certificateValue": "",
            "certificatePassword": "",
        }, properties.get("customDomainConfiguration", {}))

    def test_does_not_send_dns_suffix_when_omitted(self):
        properties = self._update_payload(hostname=None)
        self.assertNotIn("customDomainConfiguration", properties)

        properties = self._update_payload(
            hostname=None, certificate_key_vault_url="https://vault.vault.azure.net/secrets/certificate")
        self.assertNotIn("dnsSuffix", properties.get("customDomainConfiguration", {}))
        self.assertEqual("https://vault.vault.azure.net/secrets/certificate",
                         properties["customDomainConfiguration"]["certificateKeyVaultProperties"]["keyVaultUrl"])
