# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from azext_aimanager import custom
from azext_aimanager.constants import AIMANAGER_CALLER_ROLE_IDS

SUB_PATCH = "azure.cli.core.commands.client_factory.get_subscription_id"

AIMANAGER_SCOPE = ("/subscriptions/sub/resourceGroups/rg"
                   "/providers/Microsoft.ContainerService/aiManagers/aim")
NAMESPACE_SCOPE = AIMANAGER_SCOPE + "/namespaces/team-alpha"


class TestCallerRoleWiring(unittest.TestCase):

    def setUp(self):
        self.cmd = SimpleNamespace(cli_ctx=object())
        self.client = MagicMock()
        self.client.get.side_effect = ResourceNotFoundError()  # resource does not already exist

    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles")
    @patch.object(custom, "_construct_aimanager", return_value=object())
    def test_create_assigns_roles_on_aimanager_scope(self, _construct, mock_assign, _sub, mock_lro):
        mock_lro.return_value = lambda poller: poller  # waiting returns the resource

        custom.create_aimanager(self.cmd, self.client, "rg", "aim", location="eastus2")

        mock_lro.assert_called_once()  # waited for creation to succeed
        mock_assign.assert_called_once()
        _cmd, scope, roles = mock_assign.call_args.args
        self.assertEqual(scope, AIMANAGER_SCOPE)
        self.assertEqual(roles, AIMANAGER_CALLER_ROLE_IDS)

    @patch.object(custom, "warn_roles_skipped_no_wait")
    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles")
    @patch.object(custom, "_construct_aimanager", return_value=object())
    def test_create_skips_roles_with_no_wait(self, _construct, mock_assign, _sub, mock_lro, mock_warn):
        custom.create_aimanager(
            self.cmd, self.client, "rg", "aim", location="eastus2", no_wait=True)

        mock_assign.assert_not_called()
        mock_lro.assert_not_called()
        mock_warn.assert_called_once()  # prints the manual-grant remediation under --no-wait
        _cmd, scope, roles = mock_warn.call_args.args
        self.assertEqual(scope, AIMANAGER_SCOPE)
        self.assertEqual(roles, AIMANAGER_CALLER_ROLE_IDS)

    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles")
    @patch.object(custom, "_construct_namespace", return_value=object())
    def test_namespace_add_assigns_roles_on_namespace_scope(self, _construct, mock_assign, _sub, mock_lro):
        mock_lro.return_value = lambda poller: poller

        custom.add_aimanager_namespace(self.cmd, self.client, "rg", "aim", "team-alpha")

        mock_lro.assert_called_once()
        mock_assign.assert_called_once()
        _cmd, scope, roles = mock_assign.call_args.args
        self.assertEqual(scope, NAMESPACE_SCOPE)
        self.assertEqual(roles, AIMANAGER_CALLER_ROLE_IDS)

    @patch.object(custom, "warn_roles_skipped_no_wait")
    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles")
    @patch.object(custom, "_construct_namespace", return_value=object())
    def test_namespace_add_skips_roles_with_no_wait(self, _construct, mock_assign, _sub, mock_lro, mock_warn):
        custom.add_aimanager_namespace(
            self.cmd, self.client, "rg", "aim", "team-alpha", no_wait=True)

        mock_assign.assert_not_called()
        mock_lro.assert_not_called()
        mock_warn.assert_called_once()  # prints the manual-grant remediation under --no-wait
        _cmd, scope, roles = mock_warn.call_args.args
        self.assertEqual(scope, NAMESPACE_SCOPE)
        self.assertEqual(roles, AIMANAGER_CALLER_ROLE_IDS)

    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles", side_effect=RuntimeError("role setup failed"))
    @patch.object(custom, "_construct_aimanager", return_value=object())
    def test_create_does_not_fail_when_role_assignment_errors(self, _construct, _assign, _sub, mock_lro):
        mock_lro.return_value = lambda poller: "created-resource"

        # A successful create must not fail because the (best-effort) role grant blew up.
        result = custom.create_aimanager(self.cmd, self.client, "rg", "aim", location="eastus2")

        self.assertEqual(result, "created-resource")

    @patch.object(custom, "LongRunningOperation")
    @patch(SUB_PATCH, return_value="sub")
    @patch.object(custom, "assign_caller_roles")
    @patch.object(custom, "_construct_aimanager", return_value=object())
    def test_create_surfaces_lro_failure_and_skips_grant(self, _construct, mock_assign, _sub, mock_lro):
        def _raise(_poller):
            raise HttpResponseError(message="provisioning failed")
        mock_lro.return_value = _raise

        # A failed create must surface the error and must not grant roles.
        with self.assertRaises(HttpResponseError):
            custom.create_aimanager(self.cmd, self.client, "rg", "aim", location="eastus2")
        mock_assign.assert_not_called()


if __name__ == '__main__':
    unittest.main()
