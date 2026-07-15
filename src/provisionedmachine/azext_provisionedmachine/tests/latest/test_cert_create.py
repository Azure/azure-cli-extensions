# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for the ``az provisionedmachine ssh-cert-create`` command.

All external dependencies (RBAC, Key Vault, key generation) are mocked.
Tests verify the orchestration logic, input validation, PIM-derived expiry,
error handling, cleanup on failure, and correct return shape.
"""

import os
import tempfile
import unittest
from unittest import mock

from azure.cli.core import azclierror
from azext_provisionedmachine.aaz.latest.provisionedmachine._ssh_cert_create import SshCertCreate


# Convenience: a valid ARM resource ID used across tests.
_VALID_RESOURCE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/myRG/providers/Microsoft.ProvisionedMachine"
    "/machines/myDevice"
)
_VALID_VAULT = "myKeyVault"


def _make_cmd():
    """Return a mock CLI cmd object that satisfies cmd.cli_ctx access."""
    cmd = mock.Mock()
    cmd.cli_ctx = mock.Mock()
    return cmd


def _call_ssh_cert_create(cmd, vault_name, resource_id, cert_path=None, private_key_path=None):
    """Call the AAZ command's internal method directly for testing."""
    # _execute_ssh_cert_create uses 'self' as 'cmd' (accessing self.cli_ctx),
    # so passing a mock cmd object as 'self' works correctly.
    return SshCertCreate._execute_ssh_cert_create(cmd, vault_name, resource_id, cert_path, private_key_path)


class TestSshCertCreateValidation(unittest.TestCase):
    """Input validation tests."""

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_resource_id')
    def test_invalid_resource_id_raises(self, mock_validate_rid, mock_validate_vn):
        mock_validate_rid.side_effect = azclierror.InvalidArgumentValueError("bad id")
        cmd = _make_cmd()

        with self.assertRaises(azclierror.InvalidArgumentValueError):
            _call_ssh_cert_create(cmd, _VALID_VAULT, "bad-id")

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_resource_id')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_vault_name')
    def test_invalid_vault_name_raises(self, mock_validate_vn, mock_validate_rid):
        mock_validate_vn.side_effect = azclierror.InvalidArgumentValueError("bad vault")
        cmd = _make_cmd()

        with self.assertRaises(azclierror.InvalidArgumentValueError):
            _call_ssh_cert_create(cmd, "-bad-vault!", _VALID_RESOURCE_ID)


class TestSshCertCreateHappyPath(unittest.TestCase):
    """Full happy-path tests with all external calls mocked."""

    def _setup_mocks(self):
        self.keys_dir = tempfile.mkdtemp(prefix="azssh_test_")
        self.priv_path = os.path.join(self.keys_dir, "id_rsa.pem")
        self.pub_path = self.priv_path + ".pub"
        with open(self.priv_path, "w", encoding="utf-8") as f:
            f.write("-----BEGIN PRIVATE KEY-----\nFAKE\n-----END PRIVATE KEY-----\n")
        with open(self.pub_path, "w", encoding="utf-8") as f:
            f.write("ssh-rsa AAAAFAKEPUBLICKEY user@host")

        self.cert_dir = tempfile.mkdtemp(prefix="azssh_cert_test_")
        self.cert_path = os.path.join(self.cert_dir, "ssh-cert.pub")
        with open(self.cert_path, "w", encoding="utf-8") as f:
            f.write("ssh-rsa AAAAFAKEPUBLICKEY signed-blob")

    def tearDown(self):
        import shutil
        for d in [getattr(self, 'keys_dir', None), getattr(self, 'cert_dir', None)]:
            if d and os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.extract_device_id')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_resource_id')
    def test_happy_path(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                        mock_keygen, mock_sign, mock_device_id):
        self._setup_mocks()
        cmd = _make_cmd()

        mock_device_id.return_value = "myDevice"
        mock_user.return_value = "user"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}],
                                 "2026-05-26T10:00:00Z", "2026-05-26T14:00:00Z")
        mock_role.return_value = "Provisioned Machine Contributor"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {"certificatePath": self.cert_path}

        result = _call_ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        self.assertIn("privateKeyPath", result)
        self.assertIn("certificatePath", result)

        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["username"], "user")
        self.assertEqual(metadata["role"], "Provisioned Machine Contributor")
        self.assertEqual(metadata["deviceId"], "myDevice")
        self.assertEqual(metadata["startTime"], "2026-05-26T10:00:00Z")
        self.assertEqual(metadata["endTime"], "2026-05-26T14:00:00Z")


class TestSshCertCreateCleanupOnFailure(unittest.TestCase):
    """Verify ephemeral files are cleaned up when signing fails."""

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.extract_device_id')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.cleanup_ephemeral_files')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.validate_resource_id')
    def test_cleanup_on_sign_failure(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                                     mock_keygen, mock_sign, mock_cleanup, mock_device_id):
        cmd = _make_cmd()
        mock_device_id.return_value = "myDevice"

        keys_dir = tempfile.mkdtemp(prefix="azssh_test_")
        priv = os.path.join(keys_dir, "id_rsa.pem")
        pub = priv + ".pub"
        for p in (priv, pub):
            with open(p, "w") as f:
                f.write("key-content")

        mock_user.return_value = "user"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}],
                                 "2026-05-26T10:00:00Z", "2026-05-26T14:00:00Z")
        mock_role.return_value = "Provisioned Machine Admin"
        mock_keygen.return_value = (priv, pub)
        mock_sign.side_effect = azclierror.CLIInternalError("KV failed")

        with self.assertRaises(azclierror.CLIInternalError):
            _call_ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        mock_cleanup.assert_called_once()

        import shutil
        shutil.rmtree(keys_dir, ignore_errors=True)


class TestSshCertCreateRoleDerivation(unittest.TestCase):
    """Verify the correct role flows through to the metadata."""


if __name__ == '__main__':
    unittest.main()
