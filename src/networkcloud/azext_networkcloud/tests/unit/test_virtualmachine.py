# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from abc import ABC
from unittest import mock

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.custom_arguments import AAZFileStringArgFormat
from azext_networkcloud.operations.virtualmachine.console import (
    Create,
    Delete,
    Show,
    Update,
    VirtualMachineConsole,
)
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli

from .test_common_ssh import TestCommonSsh


class TestVirtualMachineConsole(unittest.TestCase):
    """
    Test VirtualMachineConsole methods.
    """

    def setUp(self):
        """Create an instance of VirtualMachineConsole."""
        self.cmd = VirtualMachineConsole()

    def test_build_arguments_schema(self):
        """Test that _build_arguments_schema unregisters the command."""
        args_schema = mock.Mock()
        results_args_schema = self.cmd._build_arguments_schema(args_schema)
        self.assertFalse(results_args_schema.console_name._registered)
        self.assertFalse(results_args_schema.console_name._required)

    def test_pre_operations(self):
        """
        Test that pre_operations sets the console name argument
        to default.
        """
        args = mock.Mock()
        result_args = self.cmd.pre_operations(args)
        self.assertEqual(result_args.console_name, "default")


class VirtualMachineConsoleCallBackTestBase(ABC):
    """
    Provides tests for classes that extend the VirtualMachineConsole class.
    """

    def test_pre_operations(self):
        """
        Test that pre_operations changes the virtual machine console name to
        default.
        """
        # Mock CLI args
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = mock.Mock()

        result_args = self.cmd.pre_operations()
        self.assertEqual(result_args.console_name, "default")


class TestVirtualMachineConsoleCreate(
    unittest.TestCase, VirtualMachineConsoleCallBackTestBase
):
    """
    This test case uses the VirtualMachineConsoleCallBackTestBase class
    to ensure the VirtualMachineConsoleCreate command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to VirtualMachineConsoleCreate."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Create(loader=self._loader, cli_ctx=self._cli_ctx)

    def test_build_arguments_schema(self):
        """
        Test that build_arguments_schema changes the ssh_public_key argument format
        """
        # Mock CLI args
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = mock.Mock()

        result_args = self.cmd._build_arguments_schema()
        self.assertIsInstance(result_args.ssh_public_key._fmt, AAZFileStringArgFormat)


class TestVirtualMachineConsoleDelete(
    unittest.TestCase, VirtualMachineConsoleCallBackTestBase
):
    """
    This test case uses the VirtualMachineConsoleCallBackTestBase class
    to ensure the VirtualMachineConsoleDelete command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to VirtualMachineConsoleDelete."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Delete(loader=self._loader, cli_ctx=self._cli_ctx)


class TestVirtualMachineConsoleShow(
    unittest.TestCase, VirtualMachineConsoleCallBackTestBase
):
    """
    This test case uses the VirtualMachineConsoleCallBackTestBase class
    to ensure the VirtualMachineConsoleShow command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to VirtualMachineConsoleShow."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Show(loader=self._loader, cli_ctx=self._cli_ctx)


class TestVirtualMachineConsoleUpdate(
    unittest.TestCase, VirtualMachineConsoleCallBackTestBase
):
    """
    This test case uses the VirtualMachineConsoleCallBackTestBase class
    to ensure the VirtualMachineConsoleUpdate command sets the metrics
    configuration name argument to default.
    """

    def setUp(self):
        """Set command to VirtualMachineConsoleUpdate."""
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = Update(loader=self._loader, cli_ctx=self._cli_ctx)

    def test_build_arguments_schema(self):
        """
        Test that build_arguments_schema changes the ssh_public_key argument format
        """
        # Mock CLI args
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = mock.Mock()

        result_args = self.cmd._build_arguments_schema()
        self.assertIsInstance(result_args.ssh_public_key._fmt, AAZFileStringArgFormat)


class TestVirtualMachineCreate(unittest.TestCase):
    def setUp(self):
        self._cli_ctx = DummyCli()
        loader = NetworkcloudCommandsLoader(self._cli_ctx)
        self._cmd = AzCliCommand(loader, "test", None)

    @mock.patch("azure.cli.core.keys.generate_ssh_keys")
    @mock.patch("os.path.expanduser")
    def test_vm_generate_ssh_keys(self, mock_expand_user, mock_keys):
        TestCommonSsh.validate_generate_ssh_keys(self, mock_expand_user, mock_keys)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    def test_get_ssh_keys_from_path(self, mock_isfile, mock_isdir, mock_listdir):
        TestCommonSsh.validate_get_ssh_keys_from_path(
            self, mock_isfile, mock_isdir, mock_listdir
        )

    def test_add_key_action(self):
        TestCommonSsh.validate_add_key_action(self)
