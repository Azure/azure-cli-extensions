# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from abc import ABC
from unittest import mock

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.kubernetescluster._create import Create
from .test_common_ssh import TestCommonSsh

from azext_networkcloud.operations.common_ssh import CustomSshOptions
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from azure.cli.core.azclierror import InvalidArgumentValueError


class TestKubernetesClusterCreate(unittest.TestCase):
    """
    Test KubernetesClusterCreate methods
    """

    def setUp(self):
        self._cli_ctx = DummyCli()
        loader = NetworkcloudCommandsLoader(self._cli_ctx)
        self.cmd = Create(loader)

    def test_build_arguments_schema(self):
        """Test that _build_arguments_schema unregisters the parameters."""
        args_schema = mock.Mock()

        results_args_schema = self.cmd._build_arguments_schema(args_schema)

        # validate the ssh-key-values parameter exists at root and child level
        self.assertIsNotNone(results_args_schema.ssh_key_values)
        self.assertIsNotNone(
            results_args_schema.control_plane_node_configuration.ssh_key_values)
        self.assertIsNotNone(
            results_args_schema.initial_agent_pool_configurations.Element.ssh_key_values)

        # valdiate registered parameters
        self.assertFalse(results_args_schema.ssh_public_keys._registered)
        self.assertFalse(
            results_args_schema.initial_agent_pool_configurations.Element.ssh_public_keys._registered)
        self.assertFalse(
            results_args_schema.control_plane_node_configuration.ssh_public_keys._registered)

    def test_pre_operations(self):
        """
        Test pre_operations sets the kubernetes cluster ssh arguments at root level
        and child level(control_plane_node_configuration and initial_agent_pool_configurations)
        """
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()
        # Create mock ssh key values
        keys = []
        for _ in range(2):
            key = rsa.generate_private_key(65537, 2048)
            pub = key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
            # Convert from bytes
            keys.append(str(pub, "UTF-8"))

        # Mock data to contain only root level admin configuration provided
        args.ssh_key_values = keys
        args.control_plane_node_configuration.ssh_key_values = []
        args.initial_agent_pool_configurations = []
        args.ssh_dest_key_path = []
        args.generate_ssh_keys = []
        self.cmd.ctx.args = args

        # Call func
        self.cmd.pre_operations()
        self.assertEqual(len(args.ssh_public_keys), 2)

        # Test admin configuration in control_plane_node_configuration is updated
        args.ssh_key_values = []
        args.control_plane_node_configuration.ssh_key_values = keys
        args.initial_agent_pool_configurations = []
        self.cmd.ctx.args = args

        # Call func
        self.cmd.pre_operations()
        # Validate control_plane_node_configuration is updated
        self.assertEqual(
            len(args.control_plane_node_configuration.ssh_public_keys), 2)

        # Test admin configuration in initial-agent-pool configuration is updated
        args.ssh_key_values = []
        args.control_plane_node_configuration.ssh_key_values = []
        for x in args.initial_agent_pool_configurations:
            x.ssh_key_values = keys
        self.cmd.ctx.args = args

        # Call func
        self.cmd.pre_operations()
        # Validate initial node configuration is updated
        for x in args.initial_agent_pool_configurations:
            self.assertEqual(len(x.ssh_public_keys), 2)

    @mock.patch("azure.cli.core.keys.generate_ssh_keys")
    @mock.patch("os.path.expanduser")
    def test_vm_generate_ssh_keys(self, mock_expand_user, mock_keys):
        """ Test KubernetesCluster generate ssh key option """
        TestCommonSsh.validate_generate_ssh_keys(
            self, mock_expand_user, mock_keys)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    def test_vm_get_ssh_keys_from_path(self, mock_isfile, mock_isdir, mock_listdir):
        """ Test KubernetesCluster ssh-key-from-path paramter enabled """
        TestCommonSsh.validate_get_ssh_keys_from_path(
            self, mock_isfile, mock_isdir, mock_listdir)

    def test_vm_add_key_action(self):
        """ Test ssh key provided as input are correctly set in ssh-public-keys"""
        TestCommonSsh.validate_add_key_action(self)
