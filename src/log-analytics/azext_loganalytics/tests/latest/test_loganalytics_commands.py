# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
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
