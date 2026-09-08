# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.core.exceptions import HttpResponseError, ResourceExistsError

from azext_aimanager import _roleassignments as ra

SCOPE = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ContainerService/aiManagers/aim"
ROLE_A = "413f2675-4911-4010-be3b-c720b43a3c59"
ROLE_B = "9c77f8a7-b0b9-4462-844c-de6e66add8ba"


def _fake_params(*, role_definition_id, principal_id, principal_type):
    # Keyword-only so an unexpected/missing kwarg (e.g. a model that lacks principal_type)
    # raises TypeError instead of silently passing, unlike a lambda **kw stub.
    return {"role_definition_id": role_definition_id,
            "principal_id": principal_id, "principal_type": principal_type}


def _jwt(claims):
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


class TestAssignCallerRoles(unittest.TestCase):

    def setUp(self):
        self.cmd = SimpleNamespace(cli_ctx=object())

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_assigns_both_roles_at_scope(self, _ident, _sub, _sdk, mock_client):
        assignments = MagicMock()
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A, ROLE_B])

        self.assertEqual(assignments.create.call_count, 2)
        seen = []
        for call in assignments.create.call_args_list:
            scope_arg, _name, params = call.args
            self.assertEqual(scope_arg, SCOPE)
            self.assertEqual(params["principal_id"], "oid-1")
            self.assertEqual(params["principal_type"], "User")
            seen.append(params["role_definition_id"])
        self.assertTrue(any(r.endswith(ROLE_A) for r in seen))
        self.assertTrue(any(r.endswith(ROLE_B) for r in seen))

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=(None, None))
    def test_skips_when_caller_object_id_unknown(self, _ident, _sub, _sdk, mock_client):
        assignments = MagicMock()
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A])

        assignments.create.assert_not_called()

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_idempotent_when_already_assigned(self, _ident, _sub, _sdk, mock_client):
        assignments = MagicMock()
        assignments.create.side_effect = ResourceExistsError("exists")
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        # Must not raise; both roles attempted.
        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A, ROLE_B])

        self.assertEqual(assignments.create.call_count, 2)

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_existing_first_role_does_not_block_second(self, _ident, _sub, _sdk, mock_client):
        assignments = MagicMock()
        # Role A was already assigned by the user before creation; role B is new. The "already
        # exists" response on role A must not stop role B from being assigned.
        assignments.create.side_effect = [ResourceExistsError("exists"), None]
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A, ROLE_B])

        self.assertEqual(assignments.create.call_count, 2)
        # The second call is role B, assigned independently of role A already existing.
        self.assertTrue(
            assignments.create.call_args_list[1].args[2]["role_definition_id"].endswith(ROLE_B))

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_best_effort_on_permission_denied(self, _ident, _sub, _sdk, mock_client):
        err = HttpResponseError()
        err.error = SimpleNamespace(code="AuthorizationFailed")
        assignments = MagicMock()
        assignments.create.side_effect = err
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        # A missing roleAssignments/write permission must not fail the create.
        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A])

        self.assertEqual(assignments.create.call_count, 1)

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_retries_other_principal_type_on_mismatch(self, _ident, _sub, _sdk, mock_client):
        mismatch = HttpResponseError(message="UnmatchedPrincipalType")
        assignments = MagicMock()
        # First attempt (User) mismatches; second attempt (ServicePrincipal) succeeds.
        assignments.create.side_effect = [mismatch, None]
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A])

        self.assertEqual(assignments.create.call_count, 2)
        self.assertEqual(assignments.create.call_args_list[0].args[2]["principal_type"], "User")
        self.assertEqual(assignments.create.call_args_list[1].args[2]["principal_type"], "ServicePrincipal")

    @patch.object(ra, "get_mgmt_service_client")
    @patch.object(ra, "get_sdk", return_value=_fake_params)
    @patch.object(ra, "get_subscription_id", return_value="sub")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_propagates_matched_type_to_next_role(self, _ident, _sub, _sdk, mock_client):
        mismatch = HttpResponseError(message="UnmatchedPrincipalType")
        assignments = MagicMock()
        # Role A: User mismatches, ServicePrincipal succeeds. Role B should then start with
        # ServicePrincipal (no repeated User mismatch).
        assignments.create.side_effect = [mismatch, None, None]
        mock_client.return_value = SimpleNamespace(role_assignments=assignments)

        ra.assign_caller_roles(self.cmd, SCOPE, [ROLE_A, ROLE_B])

        self.assertEqual(assignments.create.call_count, 3)
        self.assertEqual(assignments.create.call_args_list[1].args[2]["principal_type"], "ServicePrincipal")
        self.assertEqual(assignments.create.call_args_list[2].args[2]["principal_type"], "ServicePrincipal")

    @patch("azure.cli.core._profile.Profile")
    def test_get_caller_identity_reads_user(self, mock_profile):
        token = _jwt({"oid": "oid-user", "upn": "u@contoso.com"})
        mock_profile.return_value.get_raw_token.return_value = ((None, token, None), None, None)

        object_id, principal_type = ra._get_caller_identity(object())

        self.assertEqual(object_id, "oid-user")
        self.assertEqual(principal_type, "User")

    @patch("azure.cli.core._profile.Profile")
    def test_get_caller_identity_reads_service_principal(self, mock_profile):
        token = _jwt({"oid": "oid-app", "idtyp": "app"})
        mock_profile.return_value.get_raw_token.return_value = ((None, token, None), None, None)

        object_id, principal_type = ra._get_caller_identity(object())

        self.assertEqual(object_id, "oid-app")
        self.assertEqual(principal_type, "ServicePrincipal")

    @patch("azure.cli.core._profile.Profile")
    def test_get_caller_identity_malformed_token_returns_none(self, mock_profile):
        mock_profile.return_value.get_raw_token.return_value = ((None, "not-a-jwt", None), None, None)

        object_id, principal_type = ra._get_caller_identity(object())

        self.assertIsNone(object_id)
        self.assertIsNone(principal_type)

    @patch.object(ra, "logger")
    @patch.object(ra, "_get_caller_identity", return_value=("oid-1", "User"))
    def test_warn_roles_skipped_no_wait_prints_exact_commands(self, _ident, mock_logger):
        ra.warn_roles_skipped_no_wait(self.cmd, SCOPE, [ROLE_A, ROLE_B])

        mock_logger.warning.assert_called_once()
        fmt, *args = mock_logger.warning.call_args.args
        msg = fmt % tuple(args)
        # One runnable command per role, targeting the caller's object id and the scope.
        self.assertEqual(msg.count("az role assignment create --assignee-object-id oid-1"), 2)
        self.assertIn(f"--scope {SCOPE}", msg)
        self.assertIn(f'--role "{ra.AIMANAGER_ROLE_NAMES[ROLE_A]}"', msg)
        self.assertIn(f'--role "{ra.AIMANAGER_ROLE_NAMES[ROLE_B]}"', msg)
        # The old, broken remediation must not reappear.
        self.assertNotIn("Re-run without --no-wait", msg)
        # Sets expectations that the manual grant needs elevated permissions.
        self.assertIn("Owner or User Access Administrator", msg)

    @patch.object(ra, "logger")
    @patch.object(ra, "_get_caller_identity", return_value=(None, None))
    def test_warn_roles_skipped_no_wait_falls_back_when_oid_unknown(self, _ident, mock_logger):
        ra.warn_roles_skipped_no_wait(self.cmd, SCOPE, [ROLE_A])

        mock_logger.warning.assert_called_once()
        fmt, *args = mock_logger.warning.call_args.args
        msg = fmt % tuple(args)
        self.assertIn("--assignee-object-id <caller-object-id>", msg)


if __name__ == '__main__':
    unittest.main()
