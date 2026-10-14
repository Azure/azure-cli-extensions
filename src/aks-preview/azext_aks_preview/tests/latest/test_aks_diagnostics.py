# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import azext_aks_preview.aks_diagnostics as commands
from knack.util import CLIError


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
    def _get_aad_kubeconfig(self):
        client = mock.Mock()
        client.list_cluster_user_credentials.return_value = SimpleNamespace(
            kubeconfigs=[SimpleNamespace(value=b"apiVersion: v1\nkind: Config\n")]
        )
        with mock.patch.object(commands.tempfile, "mkstemp", return_value=(0, "test-kubeconfig")), mock.patch.object(
            commands, "print_or_merge_credentials"
        ):
            return commands._get_temp_kubeconfig_path(None, client, "rg", "cluster", True)

    def test_executes_discovered_kubelogin(self):
        executable = os.path.join(tempfile.gettempdir(), "installed tools", "kubelogin")
        with mock.patch.object(commands, "which", return_value=executable) as resolve, mock.patch.object(
            commands.subprocess, "check_output"
        ) as run:
            self.assertEqual(self._get_aad_kubeconfig(), "test-kubeconfig")
        resolve.assert_called_once_with("kubelogin")
        run.assert_called_once_with(
            [executable, "convert-kubeconfig", "--kubeconfig", "test-kubeconfig", "--login", "azurecli"],
            stderr=subprocess.STDOUT,
        )

    def test_executes_newly_installed_kubelogin_without_path_lookup(self):
        executable = os.path.join(tempfile.gettempdir(), "installed tools", "kubelogin")
        with mock.patch.object(commands, "which", return_value=None) as resolve, mock.patch.object(
            commands, "prompt_y_n", return_value=True
        ), mock.patch.object(
            commands, "_get_default_install_location", return_value=executable
        ), mock.patch.object(commands, "k8s_install_kubelogin") as install, mock.patch.object(
            commands.subprocess, "check_output"
        ) as run:
            self._get_aad_kubeconfig()
        resolve.assert_called_once_with("kubelogin")
        install.assert_called_once_with(None, "latest", executable)
        self.assertEqual(run.call_args.args[0][0], executable)

    def test_declining_installation_does_not_execute_kubelogin(self):
        with mock.patch.object(commands, "which", return_value=None), mock.patch.object(
            commands, "prompt_y_n", return_value=False
        ), mock.patch.object(commands, "k8s_install_kubelogin") as install, mock.patch.object(
            commands.subprocess, "check_output"
        ) as run:
            with self.assertRaisesRegex(CLIError, "kubelogin not found"):
                self._get_aad_kubeconfig()
        install.assert_not_called()
        run.assert_not_called()

    def test_missing_install_location_fails_without_execution(self):
        with mock.patch.object(commands, "which", return_value=None), mock.patch.object(
            commands, "prompt_y_n", return_value=True
        ), mock.patch.object(
            commands, "_get_default_install_location", return_value=None
        ), mock.patch.object(commands, "k8s_install_kubelogin") as install, mock.patch.object(
            commands.subprocess, "check_output"
        ) as run:
            with self.assertRaisesRegex(CLIError, "install location"):
                self._get_aad_kubeconfig()
        install.assert_not_called()
        run.assert_not_called()

    def test_installation_failure_does_not_execute_another_binary(self):
        with mock.patch.object(commands, "which", return_value=None), mock.patch.object(
            commands, "prompt_y_n", return_value=True
        ), mock.patch.object(
            commands, "_get_default_install_location", return_value="/installed/kubelogin"
        ), mock.patch.object(
            commands, "k8s_install_kubelogin", side_effect=CLIError("installation failed")
        ), mock.patch.object(commands.subprocess, "check_output") as run:
            with self.assertRaisesRegex(CLIError, "installation failed"):
                self._get_aad_kubeconfig()
        run.assert_not_called()

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


class TestDiagnosticsExecutablePaths(unittest.TestCase):
    def test_kollect_pins_all_cleanup_and_apply_commands(self):
        executable = os.path.join(tempfile.gettempdir(), "installed tools", "kubectl")
        client = mock.Mock()
        client.get.return_value = SimpleNamespace(
            aad_profile=None, fqdn="cluster.example", private_fqdn=None
        )
        storage_account = (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/"
            "providers/Microsoft.Storage/storageAccounts/teststorage"
        )
        with mock.patch.object(commands, "which", return_value=executable) as resolve, mock.patch.object(
            commands, "prompt_y_n", side_effect=[True, False]
        ), mock.patch.object(
            commands, "_get_temp_kubeconfig_path", return_value="test-kubeconfig"
        ), mock.patch.object(
            commands, "_generate_container_name", return_value="test-container"
        ), mock.patch.object(
            commands, "_get_cluster_features", return_value=commands.ClusterFeatures.NONE
        ), mock.patch.object(
            commands, "_get_kustomize_yaml", return_value="resources: []"
        ), mock.patch.object(commands.subprocess, "call") as cleanup, mock.patch.object(
            commands.subprocess, "check_output"
        ) as apply:
            commands.aks_kollect_cmd(
                mock.Mock(), client, "rg", "cluster", storage_account, "placeholder",
                None, None, None, None,
            )
        resolve.assert_called_once_with("kubectl")
        self.assertEqual(cleanup.call_count, 6)
        for call in cleanup.call_args_list:
            self.assertEqual(call.args[0][:4], [executable, "--kubeconfig", "test-kubeconfig", "delete"])
        apply.assert_called_once()
        self.assertEqual(apply.call_args.args[0][:5], [executable, "--kubeconfig", "test-kubeconfig", "apply", "-k"])

    def test_analysis_pins_all_query_commands(self):
        executable = os.path.join(tempfile.gettempdir(), "installed tools", "kubectl")
        with mock.patch.object(commands, "which", return_value=executable) as resolve, mock.patch.object(
            commands.subprocess, "check_output",
            side_effect=["node1 Ready", "diagnostic1", '{"Name":"node1"}', '[{"Status":"OK"}]'],
        ) as run:
            commands._display_diagnostics_report("test-kubeconfig")
        resolve.assert_called_once_with("kubectl")
        self.assertEqual(run.call_count, 4)
        for call in run.call_args_list:
            self.assertEqual(call.args[0][:3], [executable, "--kubeconfig", "test-kubeconfig"])
            self.assertTrue(call.kwargs["universal_newlines"])

    def test_missing_kubectl_fails_before_execution(self):
        with mock.patch.object(commands, "which", return_value=None), mock.patch.object(
            commands.subprocess, "check_output"
        ) as run:
            with self.assertRaisesRegex(CLIError, "kubectl executable in PATH"):
                commands._display_diagnostics_report("test-kubeconfig")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
