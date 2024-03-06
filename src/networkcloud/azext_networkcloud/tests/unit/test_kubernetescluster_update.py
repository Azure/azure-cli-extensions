# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.kubernetescluster._update import Update
from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .test_common_ssh import TestCommonSsh


class TestKubernetesClusterUpdate(unittest.TestCase):
    """
    Test KubernetesClusterUpdate methods
    """

    def setUp(self):
        self._cli_ctx = DummyCli()
        loader = NetworkcloudCommandsLoader(self._cli_ctx)
        self.cmd = Update(loader)
        # Create mock ssh key values
        self.keys = []
        for _ in range(2):
            key = rsa.generate_private_key(65537, 2048)
            pub = key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
            # Convert from bytes
            self.keys.append(str(pub, "UTF-8"))

    def test_build_arguments_schema(self):
        """Test that _build_arguments_schema unregisters the parameters."""
        args_schema = mock.Mock()
        results_args_schema = self.cmd._build_arguments_schema(args_schema)

        # validate the ssh-key-values parameter exists at root and child level
        self.assertIsNotNone(results_args_schema.ssh_key_values)
        self.assertIsNotNone(
            results_args_schema.control_plane_node_configuration.ssh_key_values
        )

        # validate unregistered parameters
        self.assertFalse(results_args_schema.ssh_public_keys._registered)
        self.assertFalse(
            results_args_schema.control_plane_node_configuration.ssh_public_keys._registered
        )

    def test_pre_operations(self):
        """
        Test pre_operations sets the kubernetes cluster ssh arguments at root level
        and child level(control_plane_node_configuration)
        """
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()

        # no ssh keys passed to agent pool
        args.ssh_key_values = AAZUndefined
        args.control_plane_node_configuration.ssh_key_values = []
        args.ssh_dest_key_path = AAZUndefined
        args.generate_ssh_keys = AAZUndefined
        args.ssh_public_keys = AAZUndefined

        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        self.cmd.pre_operations()
        self.assertEqual(
            None,
            args.ssh_public_keys,
            "no ssh keys passed - none are expected after transformation",
        )

        # Mock data to contain only root level admin configuration provided
        args.ssh_key_values = self.keys
        args.control_plane_node_configuration.ssh_key_values = []
        args.ssh_dest_key_path = AAZUndefined
        args.generate_ssh_keys = AAZUndefined
        args.ssh_public_keys = AAZUndefined
        self.cmd.ctx.args = args

        self.cmd.pre_operations()
        self.assertEqual(
            len(args.ssh_public_keys),
            len(self.keys),
            "ssh keys are expected in the cluster admin configuration",
        )

        # Test admin configuration in control_plane_node_configuration is updated
        args.control_plane_node_configuration.ssh_public_keys = None
        args.ssh_public_keys = []
        args.ssh_key_values = []
        args.control_plane_node_configuration.ssh_key_values = self.keys
        self.cmd.ctx.args = args

        self.cmd.pre_operations()
        self.assertEqual(len(args.ssh_public_keys), 0)
        self.assertEqual(
            len(args.control_plane_node_configuration.ssh_public_keys),
            len(self.keys),
            "ssh keys are expected in the control plane node configuration",
        )

        # Validate control_plane_node_configuration structure does not contain ssh_public_keys array
        # when no ssh key is provided in the input
        args.ssh_key_values = []
        args.control_plane_node_configuration.ssh_public_keys = None
        args.control_plane_node_configuration.ssh_key_values = AAZUndefined
        self.cmd.ctx.args = args

        self.cmd.pre_operations()
        self.assertEqual(len(args.ssh_public_keys), 0)
        self.assertEqual(
            None,
            args.control_plane_node_configuration.ssh_public_keys,
            "no ssh keys are expected in the control plane node configuration",
        )

        # Validate control_plane_node_configuration structure contain empty array
        # when an empty array is provided in the input
        args.ssh_key_values = []
        args.control_plane_node_configuration.ssh_public_keys = None
        args.control_plane_node_configuration.ssh_key_values = []
        self.cmd.ctx.args = args

        self.cmd.pre_operations()
        self.assertEqual(len(args.ssh_public_keys), 0)
        self.assertEqual(
            0,
            len(args.control_plane_node_configuration.ssh_public_keys),
            "no ssh keys are expected in the control plane node configuration",
        )

    @mock.patch("azure.cli.core.keys.generate_ssh_keys")
    @mock.patch("os.path.expanduser")
    def test_vm_generate_ssh_keys(self, mock_expand_user, mock_keys):
        """Test KubernetesCluster generate ssh key option"""
        TestCommonSsh.validate_generate_ssh_keys(self, mock_expand_user, mock_keys)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    def test_vm_get_ssh_keys_from_path(self, mock_isfile, mock_isdir, mock_listdir):
        """Test KubernetesCluster ssh-key-from-path parameter enabled"""
        TestCommonSsh.validate_get_ssh_keys_from_path(
            self, mock_isfile, mock_isdir, mock_listdir
        )

    def test_vm_add_key_action(self):
        """Test ssh key provided as input are correctly set in ssh-public-keys"""
        TestCommonSsh.validate_add_key_action(self)
