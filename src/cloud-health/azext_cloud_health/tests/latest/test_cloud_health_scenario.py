# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest


class CloudHealthHealthModelScenarioTest(ScenarioTest):

    def test_cloud_health_health_model_create_missing_args(self):
        """Verify create requires --name and --resource-group."""
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health health-model create')

    @patch('azext_cloud_health.custom.sdk_no_wait')
    @patch('azext_cloud_health._client_factory.get_mgmt_service_client')
    def test_cloud_health_health_model_list_by_subscription(self, mock_client_factory, mock_sdk):
        """Verify list without -g calls list_by_subscription."""
        mock_client = MagicMock()
        mock_client.health_models.list_by_subscription.return_value = []
        mock_client_factory.return_value = mock_client
        self.cmd('cloud-health health-model list')
        mock_client.health_models.list_by_subscription.assert_called_once()

    @patch('azext_cloud_health.custom.sdk_no_wait')
    @patch('azext_cloud_health._client_factory.get_mgmt_service_client')
    def test_cloud_health_health_model_list_by_rg(self, mock_client_factory, mock_sdk):
        """Verify list with -g calls list_by_resource_group."""
        mock_client = MagicMock()
        mock_client.health_models.list_by_resource_group.return_value = []
        mock_client_factory.return_value = mock_client
        self.cmd('cloud-health health-model list -g testRG')
        mock_client.health_models.list_by_resource_group.assert_called_once()


class CloudHealthEntityScenarioTest(ScenarioTest):

    def test_cloud_health_entity_create_missing_args(self):
        """Verify create requires --name, -g, and --model."""
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health entity create')


class CloudHealthSignalDefinitionScenarioTest(ScenarioTest):

    def test_cloud_health_signal_definition_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health signal-definition create')


class CloudHealthRelationshipScenarioTest(ScenarioTest):

    def test_cloud_health_relationship_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health relationship create')


class CloudHealthAuthSettingScenarioTest(ScenarioTest):

    def test_cloud_health_auth_setting_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health auth-setting create')


class CloudHealthDiscoveryRuleScenarioTest(ScenarioTest):

    def test_cloud_health_discovery_rule_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('cloud-health discovery-rule create')


if __name__ == '__main__':
    unittest.main()
