# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from azure.cli.core.azclierror import (
    ClientRequestError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
    ResourceNotFoundError,
)
from azure.core.exceptions import ResourceNotFoundError as SdkResourceNotFoundError

from azext_aks_preview import custom as aks_custom
from azext_aks_preview.alertconfiguration import (
    aks_alert_config_add_internal,
    aks_alert_config_update_internal,
)
from azext_aks_preview._format import (
    aks_alert_config_list_table_format,
    aks_alert_config_show_table_format,
)
from azext_aks_preview._validators import validate_action_group_id

VALID_ACTION_GROUP_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg"
    "/providers/Microsoft.Insights/actionGroups/myag"
)


class TestValidateActionGroupId(unittest.TestCase):
    def test_none_is_allowed(self):
        namespace = SimpleNamespace(action_group_id=None)
        validate_action_group_id(namespace)

    def test_empty_string_is_allowed(self):
        namespace = SimpleNamespace(action_group_id="")
        validate_action_group_id(namespace)

    def test_valid_action_group_id_is_allowed(self):
        namespace = SimpleNamespace(action_group_id=VALID_ACTION_GROUP_ID)
        validate_action_group_id(namespace)

    def test_valid_action_group_id_is_case_insensitive(self):
        namespace = SimpleNamespace(
            action_group_id=VALID_ACTION_GROUP_ID.replace(
                "Microsoft.Insights/actionGroups", "microsoft.insights/actiongroups"
            )
        )
        validate_action_group_id(namespace)

    def test_not_a_resource_id_is_rejected(self):
        namespace = SimpleNamespace(action_group_id="myag")
        with self.assertRaises(InvalidArgumentValueError):
            validate_action_group_id(namespace)

    def test_wrong_resource_type_is_rejected(self):
        namespace = SimpleNamespace(
            action_group_id=(
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg"
                "/providers/Microsoft.Storage/storageAccounts/mystorage"
            )
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_action_group_id(namespace)


class TestAlertConfigTableFormat(unittest.TestCase):
    def _sample(self):
        return {
            "name": "myalerts",
            "properties": {
                "mode": "Managed",
                "notification": {"actionGroupId": VALID_ACTION_GROUP_ID},
                "provisioningState": "Succeeded",
            },
        }

    def test_show_format(self):
        row = aks_alert_config_show_table_format(self._sample())
        self.assertEqual(row["name"], "myalerts")
        self.assertEqual(row["mode"], "Managed")
        self.assertEqual(row["actionGroupId"], VALID_ACTION_GROUP_ID)
        self.assertEqual(row["provisioningState"], "Succeeded")

    def test_show_format_tolerates_missing_fields(self):
        row = aks_alert_config_show_table_format({"name": "myalerts"})
        self.assertEqual(row["name"], "myalerts")
        self.assertEqual(row["mode"], "")
        self.assertEqual(row["actionGroupId"], "")
        self.assertEqual(row["provisioningState"], "")

    def test_show_format_tolerates_null_notification(self):
        row = aks_alert_config_show_table_format(
            {"name": "myalerts", "properties": {"mode": "Disabled", "notification": None}}
        )
        self.assertEqual(row["mode"], "Disabled")
        self.assertEqual(row["actionGroupId"], "")

    def test_list_format(self):
        rows = aks_alert_config_list_table_format([self._sample(), self._sample()])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "myalerts")


class TestAlertConfigAdd(unittest.TestCase):
    def _client(self):
        client = MagicMock()
        client.begin_create_or_update.return_value = "poller"
        return client

    def _sent_model(self, client):
        # begin_create_or_update(rg, cluster, name, resource, headers=...)
        return client.begin_create_or_update.call_args[0][3]

    def test_add_sends_mode_and_action_group(self):
        client = self._client()
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": "Managed",
            "action_group_id": VALID_ACTION_GROUP_ID,
        }
        aks_alert_config_add_internal(None, client, params, {}, False)

        args = client.begin_create_or_update.call_args[0]
        self.assertEqual(args[0], "rg")
        self.assertEqual(args[1], "cluster")
        self.assertEqual(args[2], "myalerts")
        model = self._sent_model(client)
        self.assertEqual(model.properties.mode, "Managed")
        self.assertEqual(model.properties.notification.action_group_id, VALID_ACTION_GROUP_ID)

    def test_add_without_action_group_sends_empty_string(self):
        client = self._client()
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": "Disabled",
            "action_group_id": None,
        }
        aks_alert_config_add_internal(None, client, params, {}, False)

        model = self._sent_model(client)
        self.assertIsNotNone(model.properties.notification)
        self.assertEqual(model.properties.notification.action_group_id, "")

    def test_add_without_name_raises(self):
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": None,
            "mode": "Managed",
            "action_group_id": None,
        }
        with self.assertRaises(RequiredArgumentMissingError):
            aks_alert_config_add_internal(None, self._client(), params, {}, False)

    def test_add_without_mode_raises(self):
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": None,
            "action_group_id": None,
        }
        with self.assertRaises(RequiredArgumentMissingError):
            aks_alert_config_add_internal(None, self._client(), params, {}, False)


class TestAlertConfigUpdate(unittest.TestCase):
    def _client_with_existing(self, mode="Managed", action_group_id=VALID_ACTION_GROUP_ID):
        client = MagicMock()
        existing = MagicMock()
        existing.properties.mode = mode
        existing.properties.notification.action_group_id = action_group_id
        client.get.return_value = existing
        client.begin_create_or_update.return_value = "poller"
        return client

    def _sent_model(self, client):
        return client.begin_create_or_update.call_args[0][3]

    def test_update_mode_only_preserves_action_group(self):
        client = self._client_with_existing()
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": "Disabled",
            "action_group_id": None,
        }
        aks_alert_config_update_internal(None, client, params, {}, False)

        model = self._sent_model(client)
        self.assertEqual(model.properties.mode, "Disabled")
        self.assertEqual(model.properties.notification.action_group_id, VALID_ACTION_GROUP_ID)

    def test_update_action_group_only_preserves_mode(self):
        client = self._client_with_existing()
        new_id = VALID_ACTION_GROUP_ID.replace("myag", "otherag")
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": None,
            "action_group_id": new_id,
        }
        aks_alert_config_update_internal(None, client, params, {}, False)

        model = self._sent_model(client)
        self.assertEqual(model.properties.mode, "Managed")
        self.assertEqual(model.properties.notification.action_group_id, new_id)

    def test_update_can_clear_action_group_with_empty_string(self):
        client = self._client_with_existing()
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": None,
            "action_group_id": "",
        }
        aks_alert_config_update_internal(None, client, params, {}, False)

        model = self._sent_model(client)
        self.assertEqual(model.properties.notification.action_group_id, "")

    def test_update_with_no_updatable_flags_raises(self):
        client = self._client_with_existing()
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": None,
            "action_group_id": None,
        }
        with self.assertRaises(RequiredArgumentMissingError):
            aks_alert_config_update_internal(None, client, params, {}, False)
        client.begin_create_or_update.assert_not_called()

    def test_update_on_missing_config_raises_cli_not_found(self):
        client = MagicMock()
        client.get.side_effect = SdkResourceNotFoundError("nope")
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": "myalerts",
            "mode": "Disabled",
            "action_group_id": None,
        }
        with self.assertRaises(ResourceNotFoundError):
            aks_alert_config_update_internal(None, client, params, {}, False)
        client.begin_create_or_update.assert_not_called()

    def test_update_without_name_raises(self):
        params = {
            "resource_group_name": "rg",
            "cluster_name": "cluster",
            "name": None,
            "mode": "Disabled",
            "action_group_id": None,
        }
        with self.assertRaises(RequiredArgumentMissingError):
            aks_alert_config_update_internal(None, MagicMock(), params, {}, False)


class TestAlertConfigCustomWrappers(unittest.TestCase):
    def test_delete_calls_begin_delete(self):
        client = MagicMock()
        aks_custom.aks_alert_config_delete(
            None, client, "rg", "cluster", "myalerts", aks_custom_headers=None, no_wait=False
        )
        args = client.begin_delete.call_args[0]
        self.assertEqual(args[0], "rg")
        self.assertEqual(args[1], "cluster")
        self.assertEqual(args[2], "myalerts")

    def test_list_calls_list_by_managed_cluster(self):
        client = MagicMock()
        aks_custom.aks_alert_config_list(None, client, "rg", "cluster")
        args = client.list_by_managed_cluster.call_args[0]
        self.assertEqual(args[0], "rg")
        self.assertEqual(args[1], "cluster")

    def test_show_calls_get(self):
        client = MagicMock()
        aks_custom.aks_alert_config_show(None, client, "rg", "cluster", "myalerts")
        args = client.get.call_args[0]
        self.assertEqual(args[0], "rg")
        self.assertEqual(args[1], "cluster")
        self.assertEqual(args[2], "myalerts")

    def test_add_rejects_existing_config(self):
        client = MagicMock()
        client.get.return_value = MagicMock()  # config already exists
        with self.assertRaises(ClientRequestError):
            aks_custom.aks_alert_config_add(
                None, client, "rg", "cluster", "myalerts", mode="Managed"
            )
        client.begin_create_or_update.assert_not_called()

    def test_add_proceeds_when_config_absent(self):
        client = MagicMock()
        client.get.side_effect = SdkResourceNotFoundError("nope")
        aks_custom.aks_alert_config_add(
            None, client, "rg", "cluster", "myalerts", mode="Managed"
        )
        client.begin_create_or_update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
