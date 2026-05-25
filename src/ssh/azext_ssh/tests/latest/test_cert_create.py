# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for the ``az ssh cert-create`` command (custom.ssh_cert_create).

All external dependencies (RBAC, Key Vault, key generation) are mocked.
Tests verify the orchestration logic, input validation, PIM-derived expiry,
error handling, cleanup on failure, and correct return shape.
"""

import os
import tempfile
import unittest
from unittest import mock

from azure.cli.core import azclierror
from azext_ssh import custom


# Convenience: a valid ARM resource ID used across tests.
_VALID_RESOURCE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/myRG/providers/Microsoft.ProvisionedMachine"
    "/machines/myDevice"
)
_VALID_VAULT = "myKeyVault"


def _make_cmd():
    """Return a mock CLI cmd object."""
    cmd = mock.Mock()
    cmd.cli_ctx = mock.Mock()
    return cmd


class TestSshCertCreateValidation(unittest.TestCase):
    """Input validation tests."""

    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_invalid_resource_id_raises(self, mock_validate_rid, mock_validate_vn):
        mock_validate_rid.side_effect = azclierror.InvalidArgumentValueError("bad id")
        cmd = _make_cmd()

        with self.assertRaises(azclierror.InvalidArgumentValueError):
            custom.ssh_cert_create(cmd, _VALID_VAULT, "bad-id")

    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    def test_invalid_vault_name_raises(self, mock_validate_vn, mock_validate_rid):
        mock_validate_vn.side_effect = azclierror.InvalidArgumentValueError("bad vault")
        cmd = _make_cmd()

        with self.assertRaises(azclierror.InvalidArgumentValueError):
            custom.ssh_cert_create(cmd, "-bad-vault!", _VALID_RESOURCE_ID)


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

    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_happy_path(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                        mock_keygen, mock_sign):
        self._setup_mocks()
        cmd = _make_cmd()

        mock_user.return_value = "user@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 4.0)
        mock_role.return_value = "Contributor"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {
            "signedCertificate": "ssh-rsa AAAA signed-blob",
            "certificatePath": self.cert_path,
        }

        result = custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        # Verify return shape — only paths returned.
        self.assertIn("privateKeyPath", result)
        self.assertIn("certificatePath", result)
        self.assertNotIn("signedCertificate", result)
        self.assertNotIn("userPrivateKey", result)
        self.assertNotIn("role", result)
        self.assertNotIn("metadata", result)

        # Verify correct metadata was passed to sign.
        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["username"], "user@contoso.com")
        self.assertEqual(metadata["role"], "Contributor")
        # Expiry should come from PIM (4.0 hours remaining)
        self.assertEqual(metadata["expiry"], 4.0)
        self.assertIn("ssh-rsa AAAAFAKEPUBLICKEY", metadata["userPublicKey"])

    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_expiry_from_pim_short(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                                    mock_keygen, mock_sign):
        """Expiry should match the remaining PIM duration (1.5h)."""
        self._setup_mocks()
        cmd = _make_cmd()

        mock_user.return_value = "user@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 1.5)
        mock_role.return_value = "Owner"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {
            "signedCertificate": "cert",
            "certificatePath": self.cert_path,
        }

        custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["expiry"], 1.5)

    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_expiry_from_pim_long(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                                   mock_keygen, mock_sign):
        """PIM with 7.25 hours remaining should pass through as-is."""
        self._setup_mocks()
        cmd = _make_cmd()

        mock_user.return_value = "user@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 7.25)
        mock_role.return_value = "Contributor"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {
            "signedCertificate": "cert",
            "certificatePath": self.cert_path,
        }

        custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["expiry"], 7.25)


class TestSshCertCreateCleanupOnFailure(unittest.TestCase):
    """Verify ephemeral files are cleaned up when signing fails."""

    @mock.patch('azext_ssh.provisioned_machine_utils.cleanup_ephemeral_files')
    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_cleanup_on_sign_failure(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                                     mock_keygen, mock_sign, mock_cleanup):
        cmd = _make_cmd()

        keys_dir = tempfile.mkdtemp(prefix="azssh_test_")
        priv = os.path.join(keys_dir, "id_rsa.pem")
        pub = priv + ".pub"
        for p in (priv, pub):
            with open(p, "w") as f:
                f.write("key-content")

        mock_user.return_value = "user@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 4.0)
        mock_role.return_value = "Owner"
        mock_keygen.return_value = (priv, pub)
        mock_sign.side_effect = azclierror.CLIInternalError("KV failed")

        with self.assertRaises(azclierror.CLIInternalError):
            custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        mock_cleanup.assert_called_once()
        cleanup_args = mock_cleanup.call_args[0]
        self.assertEqual(cleanup_args[0], priv)

        import shutil
        shutil.rmtree(keys_dir, ignore_errors=True)

    @mock.patch('azext_ssh.provisioned_machine_utils.cleanup_ephemeral_files')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_cleanup_on_role_failure(self, mock_rid, mock_vn, mock_user, mock_pim,
                                     mock_role, mock_cleanup):
        cmd = _make_cmd()

        mock_user.return_value = "user@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 4.0)
        mock_role.side_effect = azclierror.AuthenticationError("no role")

        with self.assertRaises(azclierror.AuthenticationError):
            custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        mock_cleanup.assert_called_once_with(None, None)


class TestSshCertCreateRoleDerivation(unittest.TestCase):
    """Verify the correct role flows through to the metadata."""

    def _setup_mocks(self):
        self.keys_dir = tempfile.mkdtemp(prefix="azssh_test_")
        self.priv_path = os.path.join(self.keys_dir, "id_rsa.pem")
        self.pub_path = self.priv_path + ".pub"
        with open(self.priv_path, "w") as f:
            f.write("PRIVATE")
        with open(self.pub_path, "w") as f:
            f.write("ssh-rsa PUBLIC")

        self.cert_dir = tempfile.mkdtemp(prefix="azssh_cert_test_")
        self.cert_path = os.path.join(self.cert_dir, "ssh-cert.pub")
        with open(self.cert_path, "w") as f:
            f.write("cert")

    def tearDown(self):
        import shutil
        for d in [getattr(self, 'keys_dir', None), getattr(self, 'cert_dir', None)]:
            if d and os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)

    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_owner_role_in_metadata(self, mock_rid, mock_vn, mock_user, mock_pim, mock_role,
                                    mock_keygen, mock_sign):
        self._setup_mocks()
        cmd = _make_cmd()

        mock_user.return_value = "admin@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 6.0)
        mock_role.return_value = "Owner"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {
            "signedCertificate": "cert",
            "certificatePath": self.cert_path,
        }

        custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["role"], "Owner")
        self.assertEqual(metadata["username"], "admin@contoso.com")
        self.assertEqual(metadata["expiry"], 6.0)

    @mock.patch('azext_ssh.provisioned_machine_utils.sign_certificate_metadata')
    @mock.patch('azext_ssh.provisioned_machine_utils.generate_ephemeral_keypair')
    @mock.patch('azext_ssh.provisioned_machine_utils.resolve_user_role')
    @mock.patch('azext_ssh.provisioned_machine_utils.check_pim_eligibility')
    @mock.patch('azext_ssh.provisioned_machine_utils.get_current_user_principal')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_vault_name')
    @mock.patch('azext_ssh.provisioned_machine_utils.validate_resource_id')
    def test_contributor_role_in_metadata(self, mock_rid, mock_vn, mock_user, mock_pim,
                                          mock_role, mock_keygen, mock_sign):
        self._setup_mocks()
        cmd = _make_cmd()

        mock_user.return_value = "dev@contoso.com"
        mock_pim.return_value = ([{"properties": {"assignmentType": "Activated"}}], 2.0)
        mock_role.return_value = "Contributor"
        mock_keygen.return_value = (self.priv_path, self.pub_path)
        mock_sign.return_value = {
            "signedCertificate": "cert",
            "certificatePath": self.cert_path,
        }

        result = custom.ssh_cert_create(cmd, _VALID_VAULT, _VALID_RESOURCE_ID)

        metadata = mock_sign.call_args[0][2]
        self.assertEqual(metadata["role"], "Contributor")
        self.assertEqual(metadata["expiry"], 2.0)
        self.assertEqual(result["privateKeyPath"], self.priv_path)
        self.assertEqual(result["certificatePath"], self.cert_path)


if __name__ == '__main__':
    unittest.main()
