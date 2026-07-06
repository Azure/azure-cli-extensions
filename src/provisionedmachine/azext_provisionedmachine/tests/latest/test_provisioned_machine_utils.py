# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import hashlib
import json
import os
import platform
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest import mock

from azure.cli.core import azclierror
from azext_provisionedmachine import provisioned_machine_utils as pm


class TestValidateResourceId(unittest.TestCase):
    """Tests for validate_resource_id()."""

    def test_valid_resource_id(self):
        valid_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/myRG/providers/Microsoft.ProvisionedMachine"
            "/machines/myDevice"
        )
        # Should not raise
        pm.validate_resource_id(valid_id)

    def test_valid_resource_id_mixed_case(self):
        valid_id = (
            "/Subscriptions/00000000-0000-0000-0000-000000000000"
            "/ResourceGroups/myRG/Providers/Microsoft.Compute"
            "/virtualMachines/myVM"
        )
        pm.validate_resource_id(valid_id)

    def test_invalid_resource_id_empty(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id("")

    def test_invalid_resource_id_none(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id(None)

    def test_invalid_resource_id_missing_subscriptions(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id("/resourceGroups/myRG/providers/X/Y/Z")

    def test_invalid_resource_id_no_leading_slash(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id(
                "subscriptions/00000000-0000-0000-0000-000000000000"
                "/resourceGroups/rg/providers/X/Y/Z"
            )

    def test_invalid_resource_id_extra_segments(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id(
                "/subscriptions/00000000-0000-0000-0000-000000000000"
                "/resourceGroups/rg/providers/X/Y/Z/extra/segment"
            )

    def test_invalid_resource_id_random_string(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_resource_id("just-a-random-string")


class TestValidateVaultName(unittest.TestCase):
    """Tests for validate_vault_name()."""

    def test_valid_vault_name_simple(self):
        pm.validate_vault_name("myVault01")

    def test_valid_vault_name_with_hyphens(self):
        pm.validate_vault_name("my-key-vault")

    def test_valid_vault_name_min_length(self):
        pm.validate_vault_name("abc")  # 3 chars

    def test_valid_vault_name_max_length(self):
        pm.validate_vault_name("a" + "b" * 22 + "c")  # 24 chars

    def test_invalid_vault_name_empty(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("")

    def test_invalid_vault_name_none(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name(None)

    def test_invalid_vault_name_starts_with_digit(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("1vault")

    def test_invalid_vault_name_starts_with_hyphen(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("-vault")

    def test_invalid_vault_name_ends_with_hyphen(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("vault-")

    def test_invalid_vault_name_too_short(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("ab")

    def test_invalid_vault_name_too_long(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("a" * 30)

    def test_invalid_vault_name_special_chars(self):
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            pm.validate_vault_name("vault_name!")


class TestGetCurrentUserPrincipal(unittest.TestCase):
    """Tests for get_current_user_principal()."""

    @mock.patch('azure.cli.core._profile.Profile')
    def test_returns_alias_from_upn(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_current_account_user.return_value = "user@contoso.com"

        result = pm.get_current_user_principal(cmd)
        self.assertEqual(result, "user")
        mock_profile_cls.assert_called_once_with(cli_ctx=cmd.cli_ctx)

    @mock.patch('azure.cli.core._profile.Profile')
    def test_returns_spn_unchanged(self, mock_profile_cls):
        """Service principal IDs (no '@') are returned as-is."""
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_current_account_user.return_value = "my-service-principal"

        result = pm.get_current_user_principal(cmd)
        self.assertEqual(result, "my-service-principal")

    @mock.patch('azure.cli.core._profile.Profile')
    def test_raises_when_no_user(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_current_account_user.return_value = None

        with self.assertRaises(azclierror.AuthenticationError):
            pm.get_current_user_principal(cmd)

    @mock.patch('azure.cli.core._profile.Profile')
    def test_raises_when_profile_throws(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_current_account_user.side_effect = Exception("not logged in")

        with self.assertRaises(azclierror.AuthenticationError):
            pm.get_current_user_principal(cmd)


class TestGenerateEphemeralKeypair(unittest.TestCase):
    """Tests for generate_ephemeral_keypair()."""

    @mock.patch('oschmod.set_mode')
    @mock.patch('os.path.isfile')
    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.which')
    def test_success(self, mock_which, mock_mkdtemp, mock_check_call, mock_isfile, mock_chmod):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_isfile.return_value = True
        mock_which.return_value = "/usr/bin/ssh-keygen"

        priv, pub = pm.generate_ephemeral_keypair()

        expected_priv = os.path.join("/tmp/azssh_pm_test", "id_rsa.pem")
        expected_pub = os.path.join("/tmp/azssh_pm_test", "id_rsa.pem.pub")
        self.assertEqual(priv, expected_priv)
        self.assertEqual(pub, expected_pub)
        mock_check_call.assert_called_once()
        # Verify ssh-keygen args
        call_args = mock_check_call.call_args[0][0]
        self.assertEqual(call_args[0], "/usr/bin/ssh-keygen")
        self.assertIn("-t", call_args)
        self.assertIn("rsa", call_args)
        self.assertIn("4096", call_args)
        # Verify permissions were set to 0600
        mock_chmod.assert_called_once_with(expected_priv, 0o600)

    @mock.patch('oschmod.set_mode')
    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_custom_ssh_client_folder(self, mock_mkdtemp, mock_check_call, mock_chmod):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        exe_name = "ssh-keygen.exe" if platform.system() == "Windows" else "ssh-keygen"

        with mock.patch('os.path.isfile') as mock_isfile:
            # First call: _resolve_keygen checks candidate exists → True
            # Subsequent calls: generate_ephemeral_keypair checks key files → True
            mock_isfile.return_value = True
            pm.generate_ephemeral_keypair(ssh_client_folder="/custom/path")

        call_args = mock_check_call.call_args[0][0]
        self.assertEqual(call_args[0], os.path.join("/custom/path", exe_name))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.which')
    def test_keygen_not_found(self, mock_which, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_which.return_value = "/usr/bin/ssh-keygen"
        mock_check_call.side_effect = FileNotFoundError("not found")

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("ssh-keygen not found", str(ctx.exception))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.which')
    def test_keygen_timeout(self, mock_which, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_which.return_value = "/usr/bin/ssh-keygen"
        mock_check_call.side_effect = subprocess.TimeoutExpired(cmd="keygen", timeout=30)

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("timed out", str(ctx.exception))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.which')
    def test_keygen_nonzero_exit(self, mock_which, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_which.return_value = "/usr/bin/ssh-keygen"
        mock_check_call.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="keygen"
        )

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("exited with code 1", str(ctx.exception))

    @mock.patch('os.path.isfile')
    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_keys_not_created(self, mock_mkdtemp, mock_check_call, mock_isfile):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_isfile.return_value = False  # Files don't exist after keygen

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("key files were not created", str(ctx.exception))


class TestCleanupEphemeralFiles(unittest.TestCase):
    """Tests for cleanup_ephemeral_files()."""

    def test_cleanup_files_in_temp_dir(self):
        # Create real temp files to clean up
        temp_dir = tempfile.mkdtemp(prefix="azssh_test_")
        test_file = os.path.join(temp_dir, "test_key")
        with open(test_file, "w") as f:
            f.write("secret")

        pm.cleanup_ephemeral_files(test_file)
        self.assertFalse(os.path.exists(temp_dir))

    def test_cleanup_none_path(self):
        # Should not raise
        pm.cleanup_ephemeral_files(None)

    def test_cleanup_nonexistent_path(self):
        # Should not raise
        pm.cleanup_ephemeral_files("/nonexistent/path/key")

    def test_cleanup_multiple_paths(self):
        dir1 = tempfile.mkdtemp(prefix="azssh_test_")
        dir2 = tempfile.mkdtemp(prefix="azssh_test_")
        f1 = os.path.join(dir1, "key1")
        f2 = os.path.join(dir2, "key2")
        for f in (f1, f2):
            with open(f, "w") as fh:
                fh.write("secret")

        pm.cleanup_ephemeral_files(f1, f2)
        self.assertFalse(os.path.exists(dir1))
        self.assertFalse(os.path.exists(dir2))


class TestCheckPimEligibility(unittest.TestCase):
    """Tests for check_pim_eligibility()."""

    _RESOURCE_ID = "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z"

    def _mock_response(self, status_code, json_data):
        resp = mock.Mock()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.text = json.dumps(json_data)
        return resp

    def _setup_cmd_with_profile(self, mock_oid):
        """Helper to set up cmd mock and profile mock for PIM tests."""
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        mock_oid.return_value = "oid-123"

        profile_mock = mock.Mock()
        creds_mock = mock.Mock()
        token_mock = mock.Mock()
        token_mock.token = "fake-token"
        creds_mock.get_token.return_value = token_mock
        profile_mock.get_login_credentials.return_value = (creds_mock, None, None)
        return cmd, profile_mock

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_pim_activated_passes(self, mock_profile_cls, mock_oid, mock_get):
        """Active SelfActivate/Provisioned request should pass."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [{"properties": {
                "principalId": "oid-123",
                "requestType": "SelfActivate",
                "status": "Provisioned",
                "roleDefinitionId": "/role/def/1",
                "scheduleInfo": {
                    "startDateTime": "2099-01-01T00:00:00Z",
                    "expiration": {"type": "AfterDuration", "duration": "PT4H"}
                }
            }}]
        })

        active, start_time, end_time = pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertEqual(len(active), 1)
        self.assertIn("T", start_time)
        self.assertIn("T", end_time)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_deactivated_role_blocked(self, mock_profile_cls, mock_oid, mock_get):
        """Deactivated (Revoked) activation should be rejected."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [
                {"properties": {
                    "principalId": "oid-123",
                    "requestType": "SelfActivate",
                    "status": "Provisioned",
                    "roleDefinitionId": "/role/def/1",
                    "createdOn": "2099-01-01T00:00:00Z",
                    "scheduleInfo": {
                        "startDateTime": "2099-01-01T00:00:00Z",
                        "expiration": {"type": "AfterDuration", "duration": "PT4H"}
                    }
                }},
                {"properties": {
                    "principalId": "oid-123",
                    "requestType": "SelfDeactivate",
                    "status": "Revoked",
                    "roleDefinitionId": "/role/def/1",
                    "createdOn": "2099-01-01T01:00:00Z"
                }},
            ]
        })

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertIn("expired or been deactivated", str(ctx.exception))

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_no_assignments_blocked(self, mock_profile_cls, mock_oid, mock_get):
        """No requests at all should be rejected."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {"value": []})

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertIn("No active PIM role assignment", str(ctx.exception))

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_404_raises_not_found(self, mock_profile_cls, mock_oid, mock_get):
        """Resource not found should raise ResourceNotFoundError."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(404, {"error": "not found"})

        with self.assertRaises(azclierror.ResourceNotFoundError):
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_expired_activation_blocked(self, mock_profile_cls, mock_oid, mock_get):
        """Expired activation (start + duration < now) should be rejected."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [{"properties": {
                "principalId": "oid-123",
                "requestType": "SelfActivate",
                "status": "Provisioned",
                "roleDefinitionId": "/role/def/1",
                "scheduleInfo": {
                    "startDateTime": "2020-01-01T00:00:00Z",
                    "expiration": {"type": "AfterDuration", "duration": "PT1H"}
                }
            }}]
        })

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertIn("expired or been deactivated", str(ctx.exception))


class TestResolveUserRole(unittest.TestCase):
    """Tests for resolve_user_role()."""

    def _make_pim_response(self, roles):
        """Build a fake PIM roleAssignmentScheduleInstances response.

        *roles* is a list of role display names, e.g.
        ["Provisioned Machine Admin", "Provisioned Machine Reader"].
        """
        instances = []
        for role_name in roles:
            instances.append({
                "properties": {
                    "expandedProperties": {
                        "roleDefinition": {
                            "displayName": role_name,
                        }
                    }
                }
            })
        return {"value": instances}

    def _make_cmd(self):
        """Return a mock cmd object with cli_ctx properly configured."""
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        return cmd

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_resolves_admin(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_pim_response(["Provisioned Machine Admin"])
        mock_requests_get.return_value = mock_resp

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Provisioned Machine Admin")

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_resolves_contributor(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_pim_response(["Provisioned Machine Contributor"])
        mock_requests_get.return_value = mock_resp

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Provisioned Machine Contributor")

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_resolves_reader(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        """Reader role should now succeed — restriction is device-side."""
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_pim_response(["Provisioned Machine Reader"])
        mock_requests_get.return_value = mock_resp

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Provisioned Machine Reader")

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_picks_highest_privilege(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        """When user has both Reader and Admin, Admin should win."""
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_pim_response([
            "Provisioned Machine Reader",
            "Provisioned Machine Admin",
        ])
        mock_requests_get.return_value = mock_resp

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Provisioned Machine Admin")

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_no_assignments_raises(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"value": []}
        mock_requests_get.return_value = mock_resp

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("No Provisioned Machine Reader, Contributor, or Admin", str(ctx.exception))

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_unrecognized_role_raises(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        """Assignments exist but none match Reader/Contributor/Admin."""
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_pim_response(["Storage Blob Data Processor"])
        mock_requests_get.return_value = mock_resp

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("No Provisioned Machine Reader, Contributor, or Admin", str(ctx.exception))

    @mock.patch('time.sleep')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests.get')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_current_user_object_id')
    def test_query_failure_raises(self, mock_oid, mock_profile_cls, mock_requests_get, mock_sleep):
        cmd = self._make_cmd()
        mock_oid.return_value = "oid-123"

        mock_profile = mock.Mock()
        mock_creds = mock.Mock()
        mock_token = mock.Mock()
        mock_token.token = "fake-token"
        mock_creds.get_token.return_value = mock_token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        mock_profile_cls.return_value = mock_profile

        # All 3 retry attempts fail with HTTP 500
        mock_resp = mock.Mock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {"value": []}
        mock_requests_get.return_value = mock_resp

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("No Provisioned Machine Reader, Contributor, or Admin", str(ctx.exception))


class TestGetCurrentUserObjectId(unittest.TestCase):
    """Tests for _get_current_user_object_id()."""

    def _make_jwt(self, claims):
        """Build a fake JWT with the given claims dict."""
        header = base64.urlsafe_b64encode(b'{"alg":"RS256"}').decode().rstrip("=")
        payload = base64.urlsafe_b64encode(
            json.dumps(claims).encode()
        ).decode().rstrip("=")
        signature = base64.urlsafe_b64encode(b"sig").decode().rstrip("=")
        return f"{header}.{payload}.{signature}"

    @mock.patch('azure.cli.core._profile.Profile')
    def test_extracts_oid(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile

        token = mock.Mock()
        token.token = self._make_jwt({"oid": "user-oid-123", "sub": "sub-456"})
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)

        result = pm._get_current_user_object_id(cmd)
        self.assertEqual(result, "user-oid-123")

    @mock.patch('azure.cli.core._profile.Profile')
    def test_falls_back_to_sub(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile

        token = mock.Mock()
        token.token = self._make_jwt({"sub": "sub-456"})
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)

        result = pm._get_current_user_object_id(cmd)
        self.assertEqual(result, "sub-456")

    @mock.patch('azure.cli.core._profile.Profile')
    def test_no_oid_or_sub_raises(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile

        token = mock.Mock()
        token.token = self._make_jwt({"name": "user"})  # no oid/sub
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)

        with self.assertRaises(azclierror.CLIInternalError):
            pm._get_current_user_object_id(cmd)

    @mock.patch('azure.cli.core._profile.Profile')
    def test_token_failure_raises(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_login_credentials.side_effect = Exception("not logged in")

        with self.assertRaises(azclierror.AuthenticationError):
            pm._get_current_user_object_id(cmd)


class TestIsoToEpoch(unittest.TestCase):
    """Tests for _iso_to_epoch()."""

    def test_basic(self):
        # Just verify it returns an int and the two forms match
        result = pm._iso_to_epoch("2026-05-26T10:00:00Z")
        self.assertIsInstance(result, int)

    def test_z_and_offset_match(self):
        r1 = pm._iso_to_epoch("2026-05-26T10:00:00Z")
        r2 = pm._iso_to_epoch("2026-05-26T10:00:00+00:00")
        self.assertEqual(r1, r2)


class TestSshWireHelpers(unittest.TestCase):
    """Tests for SSH binary encoding helpers."""

    def test_ssh_string(self):
        result = pm._ssh_string(b"ssh-rsa")
        self.assertEqual(result, struct.pack(">I", 7) + b"ssh-rsa")

    def test_ssh_mpint_small(self):
        # 65537 = 0x010001
        result = pm._ssh_mpint(65537)
        expected_data = b"\x01\x00\x01"
        self.assertEqual(result, struct.pack(">I", 3) + expected_data)

    def test_ssh_mpint_high_bit(self):
        # 128 = 0x80, high bit set → needs leading zero
        result = pm._ssh_mpint(128)
        expected_data = b"\x00\x80"
        self.assertEqual(result, struct.pack(">I", 2) + expected_data)

    def test_parse_rsa_pubkey_blob_roundtrip(self):
        e, n = 65537, 12345678901234567890
        blob = pm._encode_rsa_pubkey_blob(e, n)
        parsed_e, parsed_n = pm._parse_rsa_pubkey_blob(blob)
        self.assertEqual(parsed_e, e)
        self.assertEqual(parsed_n, n)

    def test_b64url_decode(self):
        data = b"hello"
        encoded = base64.urlsafe_b64encode(data).decode().rstrip("=")
        self.assertEqual(pm._b64url_decode(encoded), data)


class TestGetCaPublicKey(unittest.TestCase):
    """Tests for _get_ca_public_key()."""

    def _setup_cmd(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        token = mock.Mock()
        token.token = "fake-token"
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        return cmd

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_success_returns_e_n(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        # base64url encode e=65537 and a small n
        e_b64 = base64.urlsafe_b64encode(b"\x01\x00\x01").decode().rstrip("=")
        n_b64 = base64.urlsafe_b64encode(b"\x00" * 256).decode().rstrip("=")

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": {"kty": "RSA", "e": e_b64, "n": n_b64}
        }
        mock_requests.get.return_value = mock_response

        e, n = pm._get_ca_public_key(cmd, "myVault", "myDevice-ssh-ca")
        self.assertEqual(e, 65537)
        self.assertIsInstance(n, int)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_401_raises_auth_error(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response

        with self.assertRaises(azclierror.AuthenticationError):
            pm._get_ca_public_key(cmd, "myVault", "myDevice-ssh-ca")

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_404_raises_not_found(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        with self.assertRaises(azclierror.ResourceNotFoundError):
            pm._get_ca_public_key(cmd, "myVault", "myDevice-ssh-ca")


class TestKvSignDigest(unittest.TestCase):
    """Tests for _kv_sign_digest()."""

    def _setup_cmd(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        token = mock.Mock()
        token.token = "fake-token"
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        return cmd

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_success_returns_bytes(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        fake_sig = b"\x01\x02\x03"
        sig_b64 = base64.urlsafe_b64encode(fake_sig).decode().rstrip("=")

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": sig_b64}
        mock_requests.post.return_value = mock_response

        result = pm._kv_sign_digest(cmd, "myVault", "myDevice-ssh-ca", b"digest")
        self.assertEqual(result, fake_sig)

        # Verify URL contains /keys/myDevice-ssh-ca/sign
        post_url = mock_requests.post.call_args[0][0]
        self.assertIn("/keys/myDevice-ssh-ca/sign", post_url)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_401_raises_auth_error(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.AuthenticationError):
            pm._kv_sign_digest(cmd, "myVault", "myDevice-ssh-ca", b"digest")

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_empty_signature_raises(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd(mock_profile_cls)
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": ""}
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.CLIInternalError):
            pm._kv_sign_digest(cmd, "myVault", "myDevice-ssh-ca", b"digest")


class TestExtractDeviceId(unittest.TestCase):
    """Tests for extract_device_id()."""

    def test_extracts_last_segment(self):
        resource_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/myRG/providers/Microsoft.ProvisionedMachine"
            "/machines/myDevice"
        )
        self.assertEqual(pm.extract_device_id(resource_id), "myDevice")

    def test_handles_trailing_slash(self):
        resource_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/myRG/providers/Microsoft.ProvisionedMachine"
            "/machines/myDevice/"
        )
        self.assertEqual(pm.extract_device_id(resource_id), "myDevice")


class TestResolveKeygen(unittest.TestCase):
    """Tests for _resolve_keygen() platform-aware ssh-keygen discovery."""

    @mock.patch('shutil.which', return_value="/usr/bin/ssh-keygen")
    def test_found_on_path(self, mock_which):
        result = pm._resolve_keygen()
        self.assertEqual(result, "/usr/bin/ssh-keygen")
        mock_which.assert_called_once_with("ssh-keygen")

    @mock.patch('os.path.isfile', return_value=True)
    def test_custom_folder_found(self, mock_isfile):
        exe_name = "ssh-keygen.exe" if platform.system() == "Windows" else "ssh-keygen"
        result = pm._resolve_keygen(ssh_client_folder="/custom/bin")
        self.assertEqual(result, os.path.join("/custom/bin", exe_name))

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._probe_unix_keygen', return_value=None)
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.platform.system', return_value="Linux")
    @mock.patch('shutil.which', return_value=None)
    @mock.patch('os.path.isfile', return_value=False)
    def test_not_found_raises_with_install_instructions(self, mock_isfile, mock_which,
                                                         mock_system, mock_probe):
        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._resolve_keygen()
        msg = str(ctx.exception)
        self.assertIn("ssh-keygen was not found", msg)
        self.assertIn("sudo apt install openssh-client", msg)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._probe_windows_keygen', return_value=None)
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.platform.system', return_value="Windows")
    @mock.patch('shutil.which', return_value=None)
    @mock.patch('os.path.isfile', return_value=False)
    def test_not_found_windows_shows_windows_instructions(self, mock_isfile, mock_which,
                                                            mock_system, mock_probe):
        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._resolve_keygen()
        msg = str(ctx.exception)
        self.assertIn("ssh-keygen was not found", msg)
        self.assertIn("OpenSSH.Client", msg)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._probe_unix_keygen', return_value=None)
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils.platform.system', return_value="Darwin")
    @mock.patch('shutil.which', return_value=None)
    @mock.patch('os.path.isfile', return_value=False)
    def test_not_found_macos_shows_brew_instructions(self, mock_isfile, mock_which,
                                                       mock_system, mock_probe):
        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._resolve_keygen()
        msg = str(ctx.exception)
        self.assertIn("brew install openssh", msg)

    @mock.patch('shutil.which', return_value=None)
    @mock.patch('os.path.isfile')
    def test_custom_folder_fallback_to_autodetect(self, mock_isfile, mock_which):
        """If ssh-keygen not in custom folder, falls through to shutil.which."""
        # isfile returns False for the candidate, then which also returns None
        mock_isfile.return_value = False
        mock_which.return_value = None
        with mock.patch('azext_provisionedmachine.provisioned_machine_utils.platform.system', return_value="Linux"):
            with mock.patch('azext_provisionedmachine.provisioned_machine_utils._probe_unix_keygen', return_value=None):
                with self.assertRaises(azclierror.CLIInternalError):
                    pm._resolve_keygen(ssh_client_folder="/nonexistent/folder")


class TestProbeWindowsKeygen(unittest.TestCase):
    """Tests for _probe_windows_keygen()."""

    @mock.patch('os.path.isfile')
    def test_finds_in_system32_openssh(self, mock_isfile):
        def isfile_side_effect(path):
            return "System32" in path and "OpenSSH" in path
        mock_isfile.side_effect = isfile_side_effect

        with mock.patch.dict(os.environ, {"SystemRoot": r"C:\Windows"}):
            result = pm._probe_windows_keygen("ssh-keygen.exe")
        self.assertIsNotNone(result)
        self.assertIn("OpenSSH", result)

    @mock.patch('subprocess.run')
    @mock.patch('os.path.isfile', return_value=False)
    def test_falls_back_to_where_command(self, mock_isfile, mock_run):
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout=r"C:\custom\ssh-keygen.exe" + "\n",
        )
        # Make isfile return True only for the 'where' result
        mock_isfile.side_effect = lambda p: p == r"C:\custom\ssh-keygen.exe"

        with mock.patch.dict(os.environ, {"SystemRoot": r"C:\Windows",
                                          "ProgramFiles": r"C:\Program Files",
                                          "ProgramFiles(x86)": r"C:\Program Files (x86)"}):
            result = pm._probe_windows_keygen("ssh-keygen.exe")
        self.assertEqual(result, r"C:\custom\ssh-keygen.exe")

    @mock.patch('subprocess.run', side_effect=FileNotFoundError)
    @mock.patch('os.path.isfile', return_value=False)
    def test_returns_none_when_not_found(self, mock_isfile, mock_run):
        with mock.patch.dict(os.environ, {"SystemRoot": r"C:\Windows",
                                          "ProgramFiles": r"C:\Program Files",
                                          "ProgramFiles(x86)": r"C:\Program Files (x86)"}):
            result = pm._probe_windows_keygen("ssh-keygen.exe")
        self.assertIsNone(result)


class TestProbeUnixKeygen(unittest.TestCase):
    """Tests for _probe_unix_keygen()."""

    @mock.patch('os.path.isfile')
    def test_finds_usr_bin(self, mock_isfile):
        mock_isfile.side_effect = lambda p: p == "/usr/bin/ssh-keygen"
        result = pm._probe_unix_keygen()
        self.assertEqual(result, "/usr/bin/ssh-keygen")

    @mock.patch('subprocess.run')
    @mock.patch('os.path.isfile', return_value=False)
    def test_falls_back_to_which(self, mock_isfile, mock_run):
        mock_run.return_value = mock.Mock(returncode=0, stdout="/snap/bin/ssh-keygen\n")
        mock_isfile.side_effect = lambda p: p == "/snap/bin/ssh-keygen"
        result = pm._probe_unix_keygen()
        self.assertEqual(result, "/snap/bin/ssh-keygen")

    @mock.patch('subprocess.run', side_effect=FileNotFoundError)
    @mock.patch('os.path.isfile', return_value=False)
    def test_returns_none_when_not_found(self, mock_isfile, mock_run):
        result = pm._probe_unix_keygen()
        self.assertIsNone(result)


class TestOpensshInstallMessage(unittest.TestCase):
    """Tests for _openssh_install_message()."""

    def test_windows_message(self):
        msg = pm._openssh_install_message("Windows")
        self.assertIn("OpenSSH.Client", msg)
        self.assertIn("Add-WindowsCapability", msg)
        self.assertIn("winget", msg)

    def test_darwin_message(self):
        msg = pm._openssh_install_message("Darwin")
        self.assertIn("brew install openssh", msg)

    def test_linux_message(self):
        msg = pm._openssh_install_message("Linux")
        self.assertIn("sudo apt install openssh-client", msg)
        self.assertIn("sudo dnf install openssh-clients", msg)


class TestBuildCertBody(unittest.TestCase):
    """Tests for _build_cert_body()."""

    def test_produces_valid_structure(self):
        e, n = 65537, 2**2048 - 1  # fake RSA key
        ca_pub_blob = pm._encode_rsa_pubkey_blob(e, n)

        body = pm._build_cert_body(
            user_e=e, user_n=n, serial=0,
            key_id="testuser",
            principals=["username=testuser", "role=admin"],
            valid_after=1000000, valid_before=2000000,
            ca_pub_blob=ca_pub_blob,
        )

        # Body should start with the cert type string
        offset = 0
        type_len = struct.unpack(">I", body[0:4])[0]
        cert_type = body[4:4 + type_len].decode()
        self.assertEqual(cert_type, "ssh-rsa-cert-v01@openssh.com")

    def test_deterministic_except_nonce(self):
        e, n = 65537, 2**2048 - 1
        ca_pub_blob = pm._encode_rsa_pubkey_blob(e, n)

        b1 = pm._build_cert_body(e, n, 0, "id", ["p"], 100, 200, ca_pub_blob)
        b2 = pm._build_cert_body(e, n, 0, "id", ["p"], 100, 200, ca_pub_blob)
        # Nonce is random, so bodies differ
        self.assertNotEqual(b1, b2)
        # But after the nonce (offset 4+28+4=36 → skip type+nonce), remaining should match
        # (nonce is 32 bytes + 4-byte length prefix = 36 bytes after type string)
        type_len = 4 + len("ssh-rsa-cert-v01@openssh.com")
        nonce_len = 4 + 32
        after_nonce_1 = b1[type_len + nonce_len:]
        after_nonce_2 = b2[type_len + nonce_len:]
        self.assertEqual(after_nonce_1, after_nonce_2)


class TestAssembleOpensshCert(unittest.TestCase):
    """Tests for _assemble_openssh_cert()."""

    def test_appends_signature_block(self):
        body = b"fake-cert-body"
        sig = b"\x01\x02\x03"
        result = pm._assemble_openssh_cert(body, sig)

        # Result should start with the body
        self.assertTrue(result.startswith(body))
        # And be longer than the body (signature added)
        self.assertGreater(len(result), len(body))

        # Parse the signature block that was appended
        sig_block = result[len(body):]
        outer_len = struct.unpack(">I", sig_block[0:4])[0]
        inner = sig_block[4:4 + outer_len]
        # First string in inner should be "rsa-sha2-512"
        algo_len = struct.unpack(">I", inner[0:4])[0]
        algo = inner[4:4 + algo_len].decode()
        self.assertEqual(algo, "rsa-sha2-512")


class TestSignCertificateMetadata(unittest.TestCase):
    """Tests for sign_certificate_metadata() with KV Sign API."""

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._kv_sign_digest')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_ca_public_key')
    def test_happy_path(self, mock_get_ca, mock_sign):
        cmd = mock.Mock()

        # Setup CA key
        ca_e, ca_n = 65537, 2**2048 - 1
        mock_get_ca.return_value = (ca_e, ca_n)

        # Return a fake signature (256 bytes for RSA-2048)
        mock_sign.return_value = b"\x00" * 256

        # Create a temp pub key file
        tmp_dir = tempfile.mkdtemp(prefix="azssh_test_")
        pub_path = os.path.join(tmp_dir, "id_rsa.pem.pub")
        # Write a real-ish ssh-rsa public key
        e_bytes = (65537).to_bytes(3, "big")
        n_bytes = (2**2048 - 1).to_bytes(257, "big")
        blob = (struct.pack(">I", 7) + b"ssh-rsa" +
                struct.pack(">I", len(e_bytes)) + e_bytes +
                struct.pack(">I", len(n_bytes)) + n_bytes)
        pub_line = f"ssh-rsa {base64.b64encode(blob).decode()} test@host"
        with open(pub_path, "w") as f:
            f.write(pub_line)

        metadata = {
            "username": "user",
            "role": "Provisioned Machine Admin",
            "deviceId": "myDevice",
            "startTime": "2026-05-26T10:00:00Z",
            "endTime": "2026-05-26T14:00:00Z",
            "publicKeyPath": pub_path,
        }

        result = pm.sign_certificate_metadata(cmd, "myVault", metadata)

        cert_path = result["certificatePath"]
        self.assertTrue(os.path.isfile(cert_path))

        # Read and verify the cert starts with the correct type
        with open(cert_path, "r") as f:
            cert_line = f.read().strip()
        self.assertTrue(cert_line.startswith("ssh-rsa-cert-v01@openssh.com "))

        mock_get_ca.assert_called_once_with(cmd, "myVault", "myDevice-ssh-ca")
        mock_sign.assert_called_once()
        # Verify digest passed to sign is SHA-512 (64 bytes)
        digest_arg = mock_sign.call_args[0][3]
        self.assertEqual(len(digest_arg), 64)

        shutil.rmtree(tmp_dir, ignore_errors=True)

    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._kv_sign_digest')
    @mock.patch('azext_provisionedmachine.provisioned_machine_utils._get_ca_public_key')
    def test_sign_failure_propagates(self, mock_get_ca, mock_sign):
        cmd = mock.Mock()
        mock_get_ca.return_value = (65537, 2**2048 - 1)
        mock_sign.side_effect = azclierror.AuthenticationError("denied")

        tmp_dir = tempfile.mkdtemp(prefix="azssh_test_")
        pub_path = os.path.join(tmp_dir, "id_rsa.pem.pub")
        e_bytes = (65537).to_bytes(3, "big")
        n_bytes = (2**2048 - 1).to_bytes(257, "big")
        blob = (struct.pack(">I", 7) + b"ssh-rsa" +
                struct.pack(">I", len(e_bytes)) + e_bytes +
                struct.pack(">I", len(n_bytes)) + n_bytes)
        with open(pub_path, "w") as f:
            f.write(f"ssh-rsa {base64.b64encode(blob).decode()} test@host")

        metadata = {
            "username": "user",
            "role": "Owner",
            "deviceId": "myDevice",
            "startTime": "2026-05-26T10:00:00Z",
            "endTime": "2026-05-26T14:00:00Z",
            "publicKeyPath": pub_path,
        }

        with self.assertRaises(azclierror.AuthenticationError):
            pm.sign_certificate_metadata(cmd, "myVault", metadata)

        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
