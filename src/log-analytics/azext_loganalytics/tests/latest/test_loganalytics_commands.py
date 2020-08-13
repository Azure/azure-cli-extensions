# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ScenarioTest


class LogAnalyticsDataClientTests(ScenarioTest):
    """Test class for Log Analytics data client."""
    def test_query(self):
        """Tests data plane query capabilities for Log Analytics."""

        query_result = self.cmd('az monitor log-analytics query -w cab864ad-d0c1-496b-bc5e-4418315621bf --analytics-query "Heartbeat | getschema"').get_output_in_json()

        desired_row = {
            'ColumnName': 'TenantId',
            'ColumnOrdinal': '0',
            'ColumnType': 'string',
            'DataType': 'System.String',
            'TableName': 'getschema'
        }

        assert len(query_result) == 29
        self.assertDictEqual(query_result[0], desired_row)
