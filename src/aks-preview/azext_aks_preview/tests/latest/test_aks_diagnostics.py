# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest import mock

import azext_aks_preview.aks_diagnostics as commands


class TestGenerateContainerName(unittest.TestCase):
    def test_generate_container_name_containing_hcp(self):
        fqdn = 'abcdef-dns-ed55ba6d.hcp.centralus.azmk8s.io'
        expected_container_name = 'abcdef-dns-ed55ba6d'
        trim_container_name = commands._generate_container_name(fqdn, None)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_generate_container_name_trailing_dash(self):
        private_fqdn = 'dns-ed55ba6ad.e48fe2bd-b4bc-4aac-bc23-29bc44154fe1.privatelink.centralus.azmk8s.io'
        expected_container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink'
        trim_container_name = commands._generate_container_name(None, private_fqdn)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_generate_container_name_not_containing_hcp(self):
        private_fqdn = 'abcdef-dns-ed55ba6d.e48fe2bd-b4bc-4aac-bc23-29bc44154fe1.privatelink.centralus.azmk8s.io'
        expected_container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privat'
        trim_container_name = commands._generate_container_name(None, private_fqdn)
        self.assertEqual(expected_container_name, trim_container_name)


class TestGetStorageAccountKey(unittest.TestCase):
    def test_mapping_sdk_model(self):
        response = {"keys": [{"value": "mapping-key"}]}

        self.assertEqual("mapping-key", commands._get_storage_account_key(response))

    def test_attribute_sdk_model(self):
        response = SimpleNamespace(keys=[SimpleNamespace(value="attribute-key")])

        self.assertEqual("attribute-key", commands._get_storage_account_key(response))


class TestGetTempKubeconfigPath(unittest.TestCase):
    def test_calls_list_cluster_user_credentials_with_keyword_only_server_fqdn(self):
        """Regression test: the SDK signature made server_fqdn/format keyword-only.

        Calling list_cluster_user_credentials(rg, name, None) as a third positional
        argument raises TypeError against the current SDK. Kollect/kanalyze must
        pass server_fqdn as a keyword argument.
        """
        kubeconfig_bytes = b"apiVersion: v1\nkind: Config\n"
        credential_results = SimpleNamespace(
            kubeconfigs=[SimpleNamespace(value=kubeconfig_bytes)]
        )

        def fake_list_cluster_user_credentials(resource_group_name, name, *, server_fqdn=None, **kwargs):
            # A real client raises TypeError if server_fqdn is passed positionally,
            # so only accepting it here as keyword-only reproduces that contract.
            self.assertEqual(resource_group_name, "rg")
            self.assertEqual(name, "cluster")
            return credential_results

        client = mock.Mock()
        client.list_cluster_user_credentials.side_effect = fake_list_cluster_user_credentials

        with mock.patch.object(commands, "print_or_merge_credentials") as mock_print_or_merge:
            path = commands._get_temp_kubeconfig_path(
                cmd=None, client=client, resource_group_name="rg", name="cluster", has_aad_profile=False
            )

        self.assertTrue(path)
        client.list_cluster_user_credentials.assert_called_once_with("rg", "cluster", server_fqdn=None)
        mock_print_or_merge.assert_called_once_with(
            path, kubeconfig_bytes.decode(encoding="UTF-8"), False, None
        )


if __name__ == "__main__":
    unittest.main()
