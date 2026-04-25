# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest


class HealthModelCoreScenarioTest(ScenarioTest):

    def test_healthmodel_health_model_create_missing_args(self):
        """Verify create requires --name and --resource-group."""
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel create')

    @patch('azext_healthmodel.custom.sdk_no_wait')
    @patch('azext_healthmodel._client_factory.get_mgmt_service_client')
    def test_healthmodel_health_model_list_by_subscription(self, mock_client_factory, mock_sdk):
        """Verify list without -g calls list_by_subscription."""
        mock_client = MagicMock()
        mock_client.health_models.list_by_subscription.return_value = []
        mock_client_factory.return_value = mock_client
        self.cmd('healthmodel list')
        mock_client.health_models.list_by_subscription.assert_called_once()

    @patch('azext_healthmodel.custom.sdk_no_wait')
    @patch('azext_healthmodel._client_factory.get_mgmt_service_client')
    def test_healthmodel_health_model_list_by_rg(self, mock_client_factory, mock_sdk):
        """Verify list with -g calls list_by_resource_group."""
        mock_client = MagicMock()
        mock_client.health_models.list_by_resource_group.return_value = []
        mock_client_factory.return_value = mock_client
        self.cmd('healthmodel list -g testRG')
        mock_client.health_models.list_by_resource_group.assert_called_once()


class HealthModelEntityScenarioTest(ScenarioTest):

    def test_healthmodel_entity_create_missing_args(self):
        """Verify create requires --name, -g, and --model."""
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel entity create')


class HealthModelSignalDefinitionScenarioTest(ScenarioTest):

    def test_healthmodel_signal_definition_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel signal-definition create')


class HealthModelRelationshipScenarioTest(ScenarioTest):

    def test_healthmodel_relationship_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel relationship create')


class HealthModelAuthSettingScenarioTest(ScenarioTest):

    def test_healthmodel_auth_setting_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel auth-setting create')


class HealthModelDiscoveryRuleScenarioTest(ScenarioTest):

    def test_healthmodel_discovery_rule_create_missing_args(self):
        with self.assertRaises(SystemExit):
            self.cmd('healthmodel discovery-rule create')


if __name__ == '__main__':
    unittest.main()
