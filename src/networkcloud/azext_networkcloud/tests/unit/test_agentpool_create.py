# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.kubernetescluster.agentpool._create import Create
from azure.cli.core.mock import DummyCli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .test_common_ssh import TestCommonSsh


class TestKubernetesClusterAgentPoolCreate(unittest.TestCase):
    """
    Test KubernetesCluster AgentPool Create methods
    """

    def setUp(self):
        self._cli_ctx = DummyCli()
        loader = NetworkcloudCommandsLoader(self._cli_ctx)
        self.cmd = Create(loader)

    def test_build_arguments_schema(self):
        """Test that _build_arguments_schema un-registers the parameters."""
        args_schema = mock.Mock()
        results_args_schema = self.cmd._build_arguments_schema(args_schema)
        # validate registered parameters
        self.assertFalse(results_args_schema.ssh_public_keys._registered)

    def test_pre_operations(self):
        """
        Test pre_operations sets ssh_public_keys argument from ssh-key-values
        """
        args = mock.Mock()
        # Mock the ssh keys
        keys = []
        for _ in range(2):
            key = rsa.generate_private_key(65537, 2048)
            pub = key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
            # Convert from bytes
            keys.append(str(pub, "UTF-8"))
        # no ssh keys passed to agent pool
        args.ssh_key_values = []
        args.ssh_dest_key_path = []
        args.generate_ssh_keys = []
        args.ssh_public_keys = None

        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Call func
        self.cmd.pre_operations()
        self.assertEqual(None, self.cmd.ctx.args.ssh_public_keys)
        # SSH keys passed to agent pool
        args.ssh_key_values = keys
        args.ssh_dest_key_path = []
        args.generate_ssh_keys = []
        args.ssh_public_keys = None

        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Call func
        self.cmd.pre_operations()
        self.assertEqual(len(self.cmd.ctx.args.ssh_public_keys), 2)

    @mock.patch("azure.cli.core.keys.generate_ssh_keys")
    @mock.patch("os.path.expanduser")
    def test_vm_generate_ssh_keys(self, mock_expand_user, mock_keys):
        """Test KubernetesCluster agentpool generate ssh key option"""
        TestCommonSsh.validate_generate_ssh_keys(self, mock_expand_user, mock_keys)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    def test_vm_get_ssh_keys_from_path(self, mock_isfile, mock_isdir, mock_listdir):
        """Test KubernetesCluster agent pool ssh-key-from-path parameter enabled"""
        TestCommonSsh.validate_get_ssh_keys_from_path(
            self, mock_isfile, mock_isdir, mock_listdir
        )

    def test_vm_add_key_action(self):
        """Test ssh key provided as input are correctly set in ssh-public-keys"""
        TestCommonSsh.validate_add_key_action(self)
