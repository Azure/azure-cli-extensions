# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

from azure.cli.core import azclierror
from azext_ssh import provisioned_machine_utils as pm


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
    def test_returns_user(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_current_account_user.return_value = "user@contoso.com"

        result = pm.get_current_user_principal(cmd)
        self.assertEqual(result, "user@contoso.com")
        mock_profile_cls.assert_called_once_with(cli_ctx=cmd.cli_ctx)

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
    def test_success(self, mock_mkdtemp, mock_check_call, mock_isfile, mock_chmod):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_isfile.return_value = True

        priv, pub = pm.generate_ephemeral_keypair()

        expected_priv = os.path.join("/tmp/azssh_pm_test", "id_rsa.pem")
        expected_pub = os.path.join("/tmp/azssh_pm_test", "id_rsa.pem.pub")
        self.assertEqual(priv, expected_priv)
        self.assertEqual(pub, expected_pub)
        mock_check_call.assert_called_once()
        # Verify ssh-keygen args
        call_args = mock_check_call.call_args[0][0]
        self.assertEqual(call_args[0], "ssh-keygen")
        self.assertIn("-t", call_args)
        self.assertIn("rsa", call_args)
        self.assertIn("4096", call_args)
        # Verify permissions were set to 0600
        mock_chmod.assert_called_once_with(expected_priv, 0o600)

    @mock.patch('oschmod.set_mode')
    @mock.patch('os.path.isfile')
    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_custom_ssh_client_folder(self, mock_mkdtemp, mock_check_call,
                                       mock_isfile, mock_chmod):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_isfile.return_value = True

        pm.generate_ephemeral_keypair(ssh_client_folder="/custom/path")

        call_args = mock_check_call.call_args[0][0]
        self.assertEqual(call_args[0], os.path.join("/custom/path", "ssh-keygen"))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_keygen_not_found(self, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_check_call.side_effect = FileNotFoundError("not found")

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("ssh-keygen not found", str(ctx.exception))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_keygen_timeout(self, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
        mock_check_call.side_effect = subprocess.TimeoutExpired(cmd="keygen", timeout=30)

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.generate_ephemeral_keypair()
        self.assertIn("timed out", str(ctx.exception))

    @mock.patch('subprocess.check_call')
    @mock.patch('tempfile.mkdtemp')
    def test_keygen_nonzero_exit(self, mock_mkdtemp, mock_check_call):
        mock_mkdtemp.return_value = "/tmp/azssh_pm_test"
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

    @mock.patch('azext_ssh.provisioned_machine_utils.requests.get')
    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_pim_activated_passes(self, mock_profile_cls, mock_oid, mock_get):
        """PIM-activated assignment should pass."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [{"properties": {
                "assignmentType": "Activated",
                "endDateTime": "2099-01-01T00:00:00Z"
            }}]
        })

        instances, start_time, end_time = pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertEqual(len(instances), 1)
        self.assertIn("T", start_time)
        self.assertIn("T", end_time)

    @mock.patch('azext_ssh.provisioned_machine_utils.requests.get')
    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_direct_assignment_blocked(self, mock_profile_cls, mock_oid, mock_get):
        """Direct/permanent assignment (Assigned) should be rejected."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [{"properties": {"assignmentType": "Assigned"}}]
        })

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertIn("direct (permanent)", str(ctx.exception))
        self.assertIn("PIM-based JIT activation is required", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests.get')
    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_no_assignments_blocked(self, mock_profile_cls, mock_oid, mock_get):
        """No assignments at all should be rejected."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {"value": []})

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertIn("No active PIM role assignment", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests.get')
    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_404_raises_not_found(self, mock_profile_cls, mock_oid, mock_get):
        """Resource not found should raise ResourceNotFoundError."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(404, {"error": "not found"})

        with self.assertRaises(azclierror.ResourceNotFoundError):
            pm.check_pim_eligibility(cmd, self._RESOURCE_ID)

    @mock.patch('azext_ssh.provisioned_machine_utils.requests.get')
    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_mixed_only_activated_returned(self, mock_profile_cls, mock_oid, mock_get):
        """When both Activated and Assigned exist, only Activated should pass."""
        cmd, profile_mock = self._setup_cmd_with_profile(mock_oid)
        mock_profile_cls.return_value = profile_mock

        mock_get.return_value = self._mock_response(200, {
            "value": [
                {"properties": {"assignmentType": "Assigned"}},
                {"properties": {"assignmentType": "Activated", "endDateTime": "2099-01-01T00:00:00Z"}},
                {"properties": {"assignmentType": "Assigned"}},
            ]
        })

        instances, start_time, end_time = pm.check_pim_eligibility(cmd, self._RESOURCE_ID)
        self.assertEqual(len(instances), 1)
        self.assertIn("T", start_time)
        self.assertIn("T", end_time)


class TestResolveUserRole(unittest.TestCase):
    """Tests for resolve_user_role()."""

    def _make_assignment(self, role_def_id):
        assignment = mock.Mock()
        assignment.role_definition_id = role_def_id
        return assignment

    def _make_role_def(self, role_name):
        role_def = mock.Mock()
        role_def.role_name = role_name
        return role_def

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_resolves_owner(self, mock_client_factory, mock_oid):
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client

        assignment = self._make_assignment("role-def-1")
        auth_client.role_assignments.list_for_scope.return_value = [assignment]
        auth_client.role_definitions.get_by_id.return_value = self._make_role_def(
            "Owner"
        )

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Owner")

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_resolves_contributor(self, mock_client_factory, mock_oid):
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client

        assignment = self._make_assignment("role-def-1")
        auth_client.role_assignments.list_for_scope.return_value = [assignment]
        auth_client.role_definitions.get_by_id.return_value = self._make_role_def(
            "Provisioned Machine Contributor"
        )

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Contributor")

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_resolves_reader(self, mock_client_factory, mock_oid):
        """Reader role should now succeed — restriction is device-side."""
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client

        assignment = self._make_assignment("role-def-1")
        auth_client.role_assignments.list_for_scope.return_value = [assignment]
        auth_client.role_definitions.get_by_id.return_value = self._make_role_def(
            "Provisioned Machine Reader"
        )

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Reader")

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_picks_highest_privilege(self, mock_client_factory, mock_oid):
        """When user has both Reader and Owner, Owner should win."""
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client

        a1 = self._make_assignment("role-def-1")
        a2 = self._make_assignment("role-def-2")
        auth_client.role_assignments.list_for_scope.return_value = [a1, a2]
        auth_client.role_definitions.get_by_id.side_effect = [
            self._make_role_def("Reader"),
            self._make_role_def("Owner"),
        ]

        result = pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertEqual(result, "Owner")

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_no_assignments_raises(self, mock_client_factory, mock_oid):
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client
        auth_client.role_assignments.list_for_scope.return_value = []

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("No role assignments", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_unrecognized_role_raises(self, mock_client_factory, mock_oid):
        """Assignments exist but none match Reader/Contributor/Admin."""
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client

        assignment = self._make_assignment("role-def-1")
        auth_client.role_assignments.list_for_scope.return_value = [assignment]
        auth_client.role_definitions.get_by_id.return_value = self._make_role_def(
            "Storage Blob Data Processor"
        )

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("No Reader, Contributor, or Owner", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils._get_current_user_object_id')
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
    def test_query_failure_raises(self, mock_client_factory, mock_oid):
        cmd = mock.Mock()
        mock_oid.return_value = "oid-123"

        auth_client = mock.Mock()
        mock_client_factory.return_value = auth_client
        auth_client.role_assignments.list_for_scope.side_effect = Exception("network error")

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm.resolve_user_role(cmd, "/subscriptions/sub/resourceGroups/rg/providers/X/Y/Z")
        self.assertIn("Failed to query role assignments", str(ctx.exception))


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


class TestBuildSigningPayload(unittest.TestCase):
    """Tests for _build_signing_payload()."""

    def test_produces_base64url_sha256_digest(self):
        metadata = {"key": "value", "num": 42}
        result = pm._build_signing_payload(metadata)

        # Verify it's a SHA-256 digest, base64url encoded, no padding
        canonical = json.dumps(
            metadata, separators=(",", ":"), sort_keys=True, ensure_ascii=True
        ).encode("utf-8")
        expected_digest = hashlib.sha256(canonical).digest()
        expected = base64.urlsafe_b64encode(expected_digest).decode("ascii").rstrip("=")
        self.assertEqual(result, expected)

    def test_deterministic(self):
        metadata = {"b": 2, "a": 1}
        r1 = pm._build_signing_payload(metadata)
        r2 = pm._build_signing_payload(metadata)
        self.assertEqual(r1, r2)

    def test_key_order_independent(self):
        m1 = {"a": 1, "b": 2}
        m2 = {"b": 2, "a": 1}
        self.assertEqual(pm._build_signing_payload(m1), pm._build_signing_payload(m2))


class TestCallKeyvaultSign(unittest.TestCase):
    """Tests for _call_keyvault_sign()."""

    def _setup_cmd_with_creds(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        token = mock.Mock()
        token.token = "fake-token"
        mock_creds = mock.Mock()
        mock_creds.get_token.return_value = token
        mock_profile.get_login_credentials.return_value = (mock_creds, None, None)
        return cmd

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_success(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)
        metadata = {"userPublicKey": "ssh-rsa AAAA...", "username": "user"}

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": "signed-value-b64"}
        mock_requests.post.return_value = mock_response

        sig, cert = pm._call_keyvault_sign(cmd, "myVault", metadata)

        self.assertEqual(sig, "signed-value-b64")
        self.assertIn("ssh-rsa AAAA...", cert)
        # Verify URL is correct
        post_url = mock_requests.post.call_args[0][0]
        self.assertIn("myVault.vault.azure.net", post_url)
        self.assertIn("/keys/ssh-ca/sign", post_url)

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_401_raises_auth_error(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.AuthenticationError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("Access denied", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_404_raises_not_found(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.ResourceNotFoundError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("ssh-ca", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_500_raises_internal_error(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("HTTP 500", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_timeout_raises(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        import requests as real_requests
        mock_requests.post.side_effect = real_requests.exceptions.Timeout("timed out")
        mock_requests.exceptions = real_requests.exceptions

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("timed out", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_connection_error_raises(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        import requests as real_requests
        mock_requests.post.side_effect = real_requests.exceptions.ConnectionError("dns fail")
        mock_requests.exceptions = real_requests.exceptions

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("Unable to connect", str(ctx.exception))

    @mock.patch('azext_ssh.provisioned_machine_utils.requests')
    @mock.patch('azure.cli.core._profile.Profile')
    def test_empty_signature_raises(self, mock_profile_cls, mock_requests):
        cmd = self._setup_cmd_with_creds(mock_profile_cls)

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": ""}
        mock_requests.post.return_value = mock_response

        with self.assertRaises(azclierror.CLIInternalError) as ctx:
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})
        self.assertIn("empty signature", str(ctx.exception))

    @mock.patch('azure.cli.core._profile.Profile')
    def test_token_failure_raises_auth(self, mock_profile_cls):
        cmd = mock.Mock()
        mock_profile = mock.Mock()
        mock_profile_cls.return_value = mock_profile
        mock_profile.get_login_credentials.side_effect = Exception("no token")

        with self.assertRaises(azclierror.AuthenticationError):
            pm._call_keyvault_sign(cmd, "myVault", {"userPublicKey": "k"})


class TestSignCertificateMetadata(unittest.TestCase):
    """Tests for sign_certificate_metadata()."""

    @mock.patch('oschmod.set_mode')
    @mock.patch('azext_ssh.provisioned_machine_utils._call_keyvault_sign')
    def test_writes_cert_file(self, mock_sign, mock_chmod):
        cmd = mock.Mock()
        mock_sign.return_value = ("sig_b64", "cert-content-here")

        metadata = {
            "userPublicKey": "ssh-rsa AAAA",
            "username": "user@contoso.com",
            "role": "Owner",
            "startTime": "2026-05-26T10:00:00Z",
            "endTime": "2026-05-26T14:00:00Z",
        }

        result = pm.sign_certificate_metadata(
            cmd, "myVault", metadata
        )

        self.assertEqual(result["signedCertificate"], "cert-content-here")
        self.assertTrue(os.path.isfile(result["certificatePath"]))
        with open(result["certificatePath"], "r") as f:
            self.assertEqual(f.read(), "cert-content-here")

        # Verify permissions were set
        mock_chmod.assert_called_once()

        # Clean up
        shutil.rmtree(os.path.dirname(result["certificatePath"]),
                       ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
