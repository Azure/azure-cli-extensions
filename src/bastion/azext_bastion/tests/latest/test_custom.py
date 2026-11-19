import importlib
import os
import sys
import types
import unittest
from unittest import mock


class BastionSshAuthTypeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
        cls.module_patches = mock.patch.dict(sys.modules, cls._get_stubbed_modules())
        cls.module_patches.start()
        cls.custom = importlib.import_module("azext_bastion.custom")

    @classmethod
    def tearDownClass(cls):
        cls.module_patches.stop()

    @staticmethod
    def _get_stubbed_modules():
        azure = types.ModuleType("azure")
        azure_cli = types.ModuleType("azure.cli")
        azure_cli_core = types.ModuleType("azure.cli.core")
        azure_cli_core.AzCommandsLoader = type("AzCommandsLoader", (), {})
        azure_cli_core_aaz = types.ModuleType("azure.cli.core.aaz")
        azure_cli_core_aaz.AAZUndefined = object()

        azure_cli_core_azclierror = types.ModuleType("azure.cli.core.azclierror")
        error_types = (
            "ValidationError", "InvalidArgumentValueError", "RequiredArgumentMissingError",
            "UnrecognizedArgumentError", "CLIInternalError", "ClientRequestError"
        )
        for error_type in error_types:
            setattr(azure_cli_core_azclierror, error_type, type(error_type, (Exception,), {}))

        azure_cli_core_commands = types.ModuleType("azure.cli.core.commands")
        azure_cli_core_commands_client_factory = types.ModuleType("azure.cli.core.commands.client_factory")
        azure_cli_core_commands_client_factory.get_subscription_id = lambda *_: "00000000-0000-0000-0000-000000000000"

        azure_mgmt = types.ModuleType("azure.mgmt")
        azure_mgmt_core = types.ModuleType("azure.mgmt.core")
        azure_mgmt_core_tools = types.ModuleType("azure.mgmt.core.tools")
        azure_mgmt_core_tools.is_valid_resource_id = lambda *_: True

        knack = types.ModuleType("knack")
        knack_log = types.ModuleType("knack.log")
        knack_help_files = types.ModuleType("knack.help_files")
        knack_log.get_logger = lambda *_: mock.Mock()
        knack_help_files.helps = {}

        bastion_aaz_module = types.ModuleType("azext_bastion.aaz.latest.network.bastion")

        class Create:  # pylint: disable=too-few-public-methods
            @classmethod
            def _build_arguments_schema(cls, *args, **kwargs):  # pylint: disable=unused-argument
                return mock.Mock()

        class Show:  # pylint: disable=too-few-public-methods
            def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
                pass

            def __call__(self, *args, **kwargs):  # pylint: disable=unused-argument
                return {}

        bastion_aaz_module.Create = Create
        bastion_aaz_module.Show = Show

        return {
            "azure": azure,
            "azure.cli": azure_cli,
            "azure.cli.core": azure_cli_core,
            "azure.cli.core.aaz": azure_cli_core_aaz,
            "azure.cli.core.azclierror": azure_cli_core_azclierror,
            "azure.cli.core.commands": azure_cli_core_commands,
            "azure.cli.core.commands.client_factory": azure_cli_core_commands_client_factory,
            "azure.mgmt": azure_mgmt,
            "azure.mgmt.core": azure_mgmt_core,
            "azure.mgmt.core.tools": azure_mgmt_core_tools,
            "knack": knack,
            "knack.log": knack_log,
            "knack.help_files": knack_help_files,
            "azext_bastion.aaz.latest.network.bastion": bastion_aaz_module,
        }

    def test_get_auth_type_args_password(self):
        self.assertEqual(
            self.custom._get_auth_type_args("password"),  # pylint: disable=protected-access
            ["-o", "PreferredAuthentications=keyboard-interactive,password", "-o", "PubkeyAuthentication=no"]
        )

    def test_ssh_password_uses_password_authentication_flags(self):
        cmd = mock.Mock(cli_ctx=mock.Mock())
        with mock.patch.object(self.custom, "_test_extension"), \
                mock.patch.object(self.custom, "_is_nativeclient_enabled", return_value=True), \
                mock.patch.object(self.custom, "_is_ipconnect_request", return_value=False), \
                mock.patch.object(self.custom, "_validate_resourceid"), \
                mock.patch.object(self.custom, "_get_bastion_endpoint", return_value="endpoint"), \
                mock.patch.object(self.custom, "_get_tunnel", return_value=mock.Mock(local_port=50022, cleanup=mock.Mock())), \
                mock.patch.object(self.custom, "_start_tunnel"), \
                mock.patch.object(self.custom, "_get_ssh_path", return_value="ssh"), \
                mock.patch.object(self.custom.threading, "Thread", return_value=mock.Mock(start=mock.Mock())), \
                mock.patch.object(self.custom.subprocess, "call") as mock_call:
            self.custom.ssh_bastion_host(
                cmd=cmd,
                auth_type="password",
                target_resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm",
                target_ip_address=None,
                resource_group_name="rg",
                bastion_host_name="bastion",
                username="testuser"
            )

        command = mock_call.call_args[0][0]
        self.assertIn("PreferredAuthentications=keyboard-interactive,password", command)
        self.assertIn("PubkeyAuthentication=no", command)

    def test_ssh_aad_uses_publickey_authentication_flags(self):
        cmd = mock.Mock(cli_ctx=mock.Mock())
        fake_azssh = mock.Mock()
        fake_azssh_utils = mock.Mock()
        fake_azssh_utils.get_ssh_cert_principals.return_value = ["aaduser"]

        with mock.patch.object(self.custom, "_test_extension"), \
                mock.patch.object(self.custom, "_is_nativeclient_enabled", return_value=True), \
                mock.patch.object(self.custom, "_is_ipconnect_request", return_value=False), \
                mock.patch.object(self.custom, "_validate_resourceid"), \
                mock.patch.object(self.custom, "_get_bastion_endpoint", return_value="endpoint"), \
                mock.patch.object(self.custom, "_get_tunnel", return_value=mock.Mock(local_port=50022, cleanup=mock.Mock())), \
                mock.patch.object(self.custom, "_start_tunnel"), \
                mock.patch.object(self.custom, "_get_ssh_path", return_value="ssh"), \
                mock.patch.object(self.custom, "_get_azext_module", side_effect=[fake_azssh, fake_azssh_utils]), \
                mock.patch.object(self.custom.tempfile, "mkdtemp", return_value="/tmp/aadsshcert"), \
                mock.patch("os.path.isdir", return_value=True), \
                mock.patch.object(self.custom.threading, "Thread", return_value=mock.Mock(start=mock.Mock())), \
                mock.patch.object(self.custom.subprocess, "call") as mock_call:
            self.custom.ssh_bastion_host(
                cmd=cmd,
                auth_type="aad",
                target_resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm",
                target_ip_address=None,
                resource_group_name="rg",
                bastion_host_name="bastion"
            )

        command = mock_call.call_args[0][0]
        self.assertIn("PreferredAuthentications=publickey", command)
        self.assertIn("PubkeyAuthentication=yes", command)
        self.assertIn("IdentitiesOnly=yes", command)


if __name__ == "__main__":
    unittest.main()
