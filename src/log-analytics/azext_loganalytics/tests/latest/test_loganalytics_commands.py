# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import unittest
from unittest.mock import MagicMock, patch

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class LogAnalyticsDataClientTests(ScenarioTest):
    """Test class for Log Analytics data client."""

    @ResourceGroupPreparer(name_prefix='cli_test_log_analytics')
    def test_query(self, resource_group):
        """Tests data plane query capabilities for Log Analytics."""
        self.kwargs.update({
            'workspace_name': self.create_random_name('clitest', 20),
            'location': "eastus",
        })

        workspace_json = self.cmd(
            "monitor log-analytics workspace create -g {rg} -n {workspace_name} --location {location} --quota 1 "
            "--level 100 --sku CapacityReservation").get_output_in_json()
        self.kwargs['workspace_customerId'] = workspace_json['customerId']

        self.cmd(
            'az monitor log-analytics query -w {workspace_customerId} '
            '--analytics-query "Heartbeat | getschema"',
            checks=[
                self.check("length(@)", 31),
                self.check("@[0]", {'ColumnName': 'TenantId', 'ColumnOrdinal': '0', 'ColumnType': 'string',
                                    'DataType': 'System.String', 'TableName': 'getschema'})
            ]
        )


class LogAnalyticsClientEndpointMappingTests(unittest.TestCase):
    """Unit tests for cloud endpoint mapping in the Log Analytics data-plane client."""

    def _make_ctx(self, cloud_name, log_analytics_resource_id=None, raise_endpoint_not_set=False):
        """Build a minimal mock context with the given cloud name and endpoint."""
        from unittest.mock import PropertyMock
        from azure.cli.core.cloud import CloudEndpointNotSetException

        endpoints = MagicMock()
        if raise_endpoint_not_set:
            type(endpoints).log_analytics_resource_id = PropertyMock(
                side_effect=CloudEndpointNotSetException("log_analytics_resource_id not set")
            )
        else:
            endpoints.log_analytics_resource_id = log_analytics_resource_id

        cloud = MagicMock()
        cloud.name = cloud_name
        cloud.endpoints = endpoints

        cli_ctx = MagicMock()
        cli_ctx.cloud = cloud

        ctx = MagicMock()
        ctx.cli_ctx = cli_ctx
        return ctx

    def _get_base_url(self, ctx):
        from azext_loganalytics.aaz.latest._clients import AAZMicrosoftOperationalinsightsDataPlaneClient
        with patch.object(
            AAZMicrosoftOperationalinsightsDataPlaneClient,
            '_retrieve_value_in_arm_cloud_metadata',
            return_value=None
        ):
            return AAZMicrosoftOperationalinsightsDataPlaneClient._build_base_url(ctx)

    def test_azure_public_cloud_endpoint(self):
        """AzureCloud should resolve to the public Log Analytics endpoint."""
        ctx = self._make_ctx('AzureCloud', 'https://api.loganalytics.io')
        self.assertEqual(self._get_base_url(ctx), 'https://api.loganalytics.io')

    def test_azure_china_cloud_endpoint(self):
        """AzureChinaCloud should resolve to the China sovereign endpoint."""
        ctx = self._make_ctx('AzureChinaCloud', 'https://api.loganalytics.azure.cn')
        self.assertEqual(self._get_base_url(ctx), 'https://api.loganalytics.azure.cn')

    def test_azure_us_government_cloud_endpoint(self):
        """AzureUSGovernment should resolve to the US Government endpoint."""
        ctx = self._make_ctx('AzureUSGovernment', 'https://api.loganalytics.us')
        self.assertEqual(self._get_base_url(ctx), 'https://api.loganalytics.us')

    def test_fallback_to_host_templates_when_endpoint_not_set(self):
        """When cloud endpoint is not configured, fall back to _CLOUD_HOST_TEMPLATES."""
        expected_by_cloud = {
            'AzureCloud': 'https://api.loganalytics.io',
            'AzureChinaCloud': 'https://api.loganalytics.azure.cn',
            'AzureUSGovernment': 'https://api.loganalytics.us',
        }
        for cloud_name, expected_url in expected_by_cloud.items():
            with self.subTest(cloud_name=cloud_name):
                ctx = self._make_ctx(cloud_name, raise_endpoint_not_set=True)
                self.assertEqual(self._get_base_url(ctx), expected_url)
