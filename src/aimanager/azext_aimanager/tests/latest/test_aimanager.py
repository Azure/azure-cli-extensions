# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from azext_aimanager import custom
from azext_aimanager import _params
from azext_aimanager.constants import AIMANAGER_CALLER_ROLE_IDS
from azext_aimanager.vendored_sdks.v2026_09_02_preview import models

SUB_PATCH = "azure.cli.core.commands.client_factory.get_subscription_id"

AIMANAGER_SCOPE = ("/subscriptions/sub/resourceGroups/rg"
                   "/providers/Microsoft.ContainerService/aiManagers/aim")
NAMESPACE_SCOPE = AIMANAGER_SCOPE + "/namespaces/team-alpha"


class _ArgumentContext:

    def __init__(self, loader, scope):
        self.loader = loader
        self.scope = scope

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def argument(self, name, **kwargs):
        self.loader.arguments[(self.scope, name)] = kwargs

    def extra(self, name, **kwargs):
        self.argument(name, **kwargs)

    def ignore(self, name):
        self.loader.arguments[(self.scope, name)] = {"ignored": True}


class _ArgumentLoader:

    def __init__(self):
        self.cli_ctx = MagicMock()
        self.arguments = {}

    def argument_context(self, scope):
        return _ArgumentContext(self, scope)


class TestAIManagerArguments(unittest.TestCase):

    @patch.object(_params, "get_location_type")
    def test_cluster_id_is_optional_on_create(self, _get_location_type):
        loader = _ArgumentLoader()

        _params.load_arguments(loader, None)

        argument = loader.arguments[("aimanager create", "cluster_id")]
        self.assertEqual(argument["options_list"], ["--cluster-id"])
        self.assertFalse(argument.get("required", False))


class TestAIManagerConstruction(unittest.TestCase):

    def test_construct_aimanager_sets_cluster_resource_id(self):
        properties_model = MagicMock()
        ai_manager = SimpleNamespace()
        cmd = MagicMock()
        cmd.get_models.side_effect = [properties_model, MagicMock(return_value=ai_manager)]

        result = custom._construct_aimanager(
            cmd, "eastus2", {"env": "test"}, "Keep", "/subscriptions/sub/clusters/aks")

        properties_model.assert_called_once_with(
            delete_policy="Keep",
            cluster_resource_id="/subscriptions/sub/clusters/aks",
        )
        self.assertIs(result, ai_manager)

    def _create(self, cluster_id=None):
        cmd = SimpleNamespace(
            cli_ctx=object(),
            get_models=lambda name, **_: getattr(models, name),
        )
        client = MagicMock()
        client.get.side_effect = ResourceNotFoundError()

        with patch.object(custom, "warn_roles_skipped_no_wait"), \
                patch(SUB_PATCH, return_value="sub"):
            custom.create_aimanager(
                cmd, client, "rg", "aim", location="eastus2",
                cluster_id=cluster_id, no_wait=True)

        return client.begin_create_or_update.call_args.args[2]

    def test_create_serializes_cluster_resource_id_when_provided(self):
        resource = self._create("/subscriptions/sub/clusters/aks")

        self.assertEqual(
            dict(resource.properties)["clusterResourceId"],
            "/subscriptions/sub/clusters/aks",
        )

    def test_create_omits_cluster_resource_id_when_not_provided(self):
        resource = self._create()

        self.assertNotIn("clusterResourceId", dict(resource.properties))

    def test_update_omits_existing_cluster_resource_id(self):
        cmd = SimpleNamespace(
            cli_ctx=object(),
            get_models=lambda name, **_: getattr(models, name),
        )
        client = MagicMock()
        client.get.return_value = models.AIManager(
            location="eastus2",
            tags={"env": "test"},
            properties=models.AIManagerProperties(
                delete_policy="Keep",
                cluster_resource_id="/subscriptions/sub/clusters/aks",
            ),
        )

        custom.update_aimanager(cmd, client, "rg", "aim", no_wait=True)

        resource = client.begin_create_or_update.call_args.args[2]
        self.assertNotIn("clusterResourceId", dict(resource.properties))
        self.assertEqual(dict(resource.properties)["deletePolicy"], "Keep")

    def test_update_rejects_cluster_id(self):
        with self.assertRaises(TypeError):
            custom.update_aimanager(
                SimpleNamespace(cli_ctx=object()), MagicMock(), "rg", "aim",
                cluster_id="/subscriptions/sub/clusters/other-aks",
            )


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
