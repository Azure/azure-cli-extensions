# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest import mock

from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError
from azure.mgmt.resource.resources.models import GenericResource

from azext_foundry_cost_control._params import (
    _parse_cost_control_connections,
    _parse_cost_control_id,
)
from azext_foundry_cost_control.custom import (
    account_update,
    deployment_create,
    deployment_update,
)


ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/"
    "resourceGroups/test-rg/providers/Microsoft.CognitiveServices/accounts/test-account"
)
COST_CONTROL_ID = ACCOUNT_ID + "/costControls/test-control"
CONNECTION_ID = ACCOUNT_ID + "/connections/test-connection"
DEPLOYMENT_ID = ACCOUNT_ID + "/deployments/test-deployment"


class FoundryCostControlCustomTest(unittest.TestCase):

    def test_parse_cost_control_connections(self):
        result = _parse_cost_control_connections(json.dumps({
            "appInsightsConnectionId": CONNECTION_ID,
            "eventGridConnectionId": None,
        }))

        self.assertEqual(result["appInsightsConnectionId"], CONNECTION_ID)
        self.assertIsNone(result["eventGridConnectionId"])

    def test_parse_cost_control_connections_rejects_unknown_property(self):
        with self.assertRaises(InvalidArgumentValueError):
            _parse_cost_control_connections('{"unsupported":"value"}')

    def test_parse_cost_control_connections_rejects_non_object(self):
        with self.assertRaises(InvalidArgumentValueError):
            _parse_cost_control_connections("[]")

    def test_parse_cost_control_id_rejects_other_resource_type(self):
        with self.assertRaises(InvalidArgumentValueError):
            _parse_cost_control_id(ACCOUNT_ID)

    @mock.patch("azext_foundry_cost_control.custom.patch_resource")
    @mock.patch("azext_foundry_cost_control.custom.resource_id", return_value=ACCOUNT_ID)
    @mock.patch("azext_foundry_cost_control.custom.get_subscription_id", return_value="subscription-id")
    def test_account_update_patches_cost_control_properties(
            self, get_subscription_id_mock, resource_id_mock, patch_resource_mock):
        cmd = mock.Mock()
        client = mock.Mock()
        connections = {"appInsightsConnectionId": CONNECTION_ID}

        result = account_update(
            cmd=cmd,
            client=client,
            resource_group_name="test-rg",
            account_name="test-account",
            cost_control_ids=[COST_CONTROL_ID],
            cost_control_connections=connections,
        )

        self.assertIs(result, patch_resource_mock.return_value)
        get_subscription_id_mock.assert_called_once_with(cmd.cli_ctx)
        resource_id_mock.assert_called_once_with(
            subscription="subscription-id",
            resource_group="test-rg",
            namespace="Microsoft.CognitiveServices",
            type="accounts",
            name="test-account",
        )
        patch_resource_mock.assert_called_once()
        patch_arguments = patch_resource_mock.call_args.kwargs
        self.assertEqual(patch_arguments["resource_ids"], [ACCOUNT_ID])
        self.assertEqual(patch_arguments["api_version"], "2026-09-15-preview")
        self.assertEqual(
            json.loads(patch_arguments["properties"]),
            {
                "costControlIds": [COST_CONTROL_ID],
                "costControlConnections": connections,
            },
        )

    @mock.patch("azext_foundry_cost_control.custom.patch_resource")
    @mock.patch("azext_foundry_cost_control.custom.core_account_update")
    def test_account_update_delegates_legacy_update(
            self, core_account_update_mock, patch_resource_mock):
        result = account_update(
            cmd=mock.Mock(),
            client=mock.Mock(),
            resource_group_name="test-rg",
            account_name="test-account",
            tags={"environment": "test"},
        )

        self.assertIs(result, core_account_update_mock.return_value)
        core_account_update_mock.assert_called_once()
        patch_resource_mock.assert_not_called()

    @mock.patch("azext_foundry_cost_control.custom.patch_resource")
    @mock.patch("azext_foundry_cost_control.custom.resource_id", return_value=ACCOUNT_ID)
    @mock.patch("azext_foundry_cost_control.custom.get_subscription_id", return_value="subscription-id")
    @mock.patch("azext_foundry_cost_control.custom.core_account_update")
    def test_account_update_waits_for_legacy_update_before_preview_patch(
            self,
            core_account_update_mock,
            _get_subscription_id_mock,
            _resource_id_mock,
            patch_resource_mock):
        poller = mock.Mock()
        core_account_update_mock.return_value = poller

        account_update(
            cmd=mock.Mock(),
            client=mock.Mock(),
            resource_group_name="test-rg",
            account_name="test-account",
            tags={"environment": "test"},
            cost_control_ids=[COST_CONTROL_ID],
        )

        poller.result.assert_called_once_with()
        patch_resource_mock.assert_called_once()

    def test_account_update_rejects_more_than_twenty_cost_controls(self):
        with self.assertRaises(InvalidArgumentValueError):
            account_update(
                cmd=mock.Mock(),
                client=mock.Mock(),
                resource_group_name="test-rg",
                account_name="test-account",
                cost_control_ids=[COST_CONTROL_ID] * 21,
            )

    def test_account_update_rejects_connections_and_clear_together(self):
        with self.assertRaises(MutuallyExclusiveArgumentError):
            account_update(
                cmd=mock.Mock(),
                client=mock.Mock(),
                resource_group_name="test-rg",
                account_name="test-account",
                cost_control_connections={"appInsightsConnectionId": CONNECTION_ID},
                clear_cost_control_connections=True,
            )

    @mock.patch("azext_foundry_cost_control.custom.update_resource")
    @mock.patch(
        "azext_foundry_cost_control.custom._deployment_resource_id",
        return_value=DEPLOYMENT_ID,
    )
    def test_deployment_create_includes_cost_control_in_put(
            self, _deployment_resource_id_mock, update_resource_mock):
        result = deployment_create(
            cmd=mock.Mock(),
            client=mock.Mock(),
            resource_group_name="test-rg",
            account_name="test-account",
            deployment_name="test-deployment",
            model_format="OpenAI",
            model_name="gpt-4.1",
            model_version="2025-04-14",
            sku_name="GlobalStandard",
            sku_capacity=10,
            cost_control_ids=[COST_CONTROL_ID],
        )

        self.assertIs(result, update_resource_mock.return_value)
        parameters = update_resource_mock.call_args.kwargs["parameters"]
        self.assertEqual(
            parameters.properties,
            {
                "model": {
                    "format": "OpenAI",
                    "name": "gpt-4.1",
                    "version": "2025-04-14",
                },
                "costControlIds": [COST_CONTROL_ID],
            },
        )
        self.assertEqual(parameters.sku, {"name": "GlobalStandard", "capacity": 10})
        self.assertEqual(
            update_resource_mock.call_args.kwargs["api_version"],
            "2026-09-15-preview",
        )

    @mock.patch("azext_foundry_cost_control.custom.core_deployment_create")
    def test_deployment_create_delegates_without_cost_control_ids(
            self, core_deployment_create_mock):
        client = mock.Mock()

        result = deployment_create(
            cmd=mock.Mock(),
            client=client,
            resource_group_name="test-rg",
            account_name="test-account",
            deployment_name="test-deployment",
            model_format="OpenAI",
            model_name="gpt-4.1",
            model_version="2025-04-14",
        )

        self.assertIs(result, core_deployment_create_mock.return_value)
        self.assertIs(
            core_deployment_create_mock.call_args.kwargs["client"],
            client,
        )

    @mock.patch("azext_foundry_cost_control.custom.update_resource")
    @mock.patch("azext_foundry_cost_control.custom.show_resource")
    @mock.patch(
        "azext_foundry_cost_control.custom._deployment_resource_id",
        return_value=DEPLOYMENT_ID,
    )
    def test_deployment_update_preserves_existing_properties(
            self,
            _deployment_resource_id_mock,
            show_resource_mock,
            update_resource_mock):
        show_resource_mock.return_value = GenericResource(
            properties={
                "model": {
                    "format": "OpenAI",
                    "name": "gpt-4.1",
                    "version": "2025-04-14",
                },
                "provisioningState": "Succeeded",
            },
            sku={"name": "GlobalStandard", "capacity": 10},
            tags={"environment": "test"},
        )

        deployment_update(
            cmd=mock.Mock(),
            resource_group_name="test-rg",
            account_name="test-account",
            deployment_name="test-deployment",
            cost_control_ids=[COST_CONTROL_ID],
        )

        parameters = update_resource_mock.call_args.kwargs["parameters"]
        self.assertEqual(
            parameters.properties["costControlIds"],
            [COST_CONTROL_ID],
        )
        self.assertEqual(parameters.properties["model"]["name"], "gpt-4.1")
        self.assertNotIn("provisioningState", parameters.properties)
        self.assertEqual(parameters.tags, {"environment": "test"})

    def test_deployment_rejects_more_than_one_cost_control(self):
        with self.assertRaises(InvalidArgumentValueError):
            deployment_create(
                cmd=mock.Mock(),
                client=mock.Mock(),
                resource_group_name="test-rg",
                account_name="test-account",
                deployment_name="test-deployment",
                model_format="OpenAI",
                model_name="gpt-4.1",
                model_version="2025-04-14",
                cost_control_ids=[COST_CONTROL_ID, COST_CONTROL_ID],
            )
