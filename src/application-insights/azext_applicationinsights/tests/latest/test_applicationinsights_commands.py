# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ScenarioTest


class ApplicationInsightsDataClientTests(ScenarioTest):
    """Test class for Application Insights data client."""
    def test_query_execute(self):
        """Tests data plane query capabilities for Application Insights."""
        self.cmd('az monitor app-insights query --apps 578f0e27-12e9-4631-bc02-50b965da2633 f4963800-c77d-40a3-8b0b-448678904c33 --analytics-query "availabilityResults | distinct name | order by name asc"', checks=[
            self.check('tables[0].rows[-1][0]', 'microsoft'),
            self.check('tables[0].rows[-2][0]', 'google')
        ])
        query_guid = self.cmd('az monitor app-insights query --app 578f0e27-12e9-4631-bc02-50b965da2633 --analytics-query "requests | getschema"').get_output_in_json()
        query_name_rg = self.cmd('az monitor app-insights query --apps ace-test -g ace-test --analytics-query "requests | getschema"').get_output_in_json()
        query_azure_id = self.cmd('az monitor app-insights query --analytics-query "requests | getschema" --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ace-test/providers/microsoft.insights/components/ace-test').get_output_in_json()
        assert query_guid == query_name_rg
        assert query_name_rg == query_azure_id
        assert len(query_guid['tables'][0]['rows']) == 37
        assert isinstance(query_guid['tables'][0]['rows'][0][1], (int, float, complex))

    def test_query_execute_with_different_offset(self):
        """Tests data plane query capabilities for Application Insights."""
        self.cmd('az monitor app-insights query --apps db709f0e-cb4e-4f43-ba80-05e10d6a4447 --analytics-query "availabilityResults | distinct name | order by name asc" --offset P3DT12H')
        self.cmd('az monitor app-insights query --apps db709f0e-cb4e-4f43-ba80-05e10d6a4447 --analytics-query "availabilityResults | distinct name | order by name asc" --offset 3d12h1m')

    def test_metrics_show(self):
        self.cmd('az monitor app-insights metrics show --app 578f0e27-12e9-4631-bc02-50b965da2633 --metrics requests/duration --aggregation count sum --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00', checks=[
            self.check('value."requests/duration".count', 0),
            self.check('value."requests/duration".sum', 0)
        ])
        result = self.cmd('az monitor app-insights metrics show --app /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ace-test/providers/microsoft.insights/components/ace-test -m availabilityResults/count --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00').get_output_in_json()
        azure_result = self.cmd('az monitor app-insights metrics show --app 578f0e27-12e9-4631-bc02-50b965da2633 --metric availabilityResults/count --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00').get_output_in_json()
        assert isinstance(result["value"]["availabilityResults/count"]['sum'], (int, float, complex))
        assert result["value"]["availabilityResults/count"]['sum'] == azure_result["value"]["availabilityResults/count"]['sum']

    def test_metrics_get_metadata(self):
        self.cmd('az monitor app-insights metrics get-metadata --app 578f0e27-12e9-4631-bc02-50b965da2633', checks=[
            self.check('dimensions."availabilityResult/location".displayName', 'Run location'),
            self.check('metrics."availabilityResults/availabilityPercentage".displayName', 'Availability'),
            self.check('metrics."users/count".supportedAggregations[0]', 'unique'),
            self.check('metrics."users/count".supportedGroupBy.all[0]', 'trace/severityLevel')
        ])

    def test_events_show(self):
        self.cmd('az monitor app-insights events show --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults --event 792aeac4-3f9a-11e9-bbeb-376e4a601afa --start-time 2019-03-05 23:00:00 +00:00 --end-time 2019-03-05 23:05:00 +00:00', checks=[
            self.check('value[0].ai.appId', '578f0e27-12e9-4631-bc02-50b965da2633'),
            self.check('value[0].availabilityResult.duration', 591),
            self.check('value[0].client.city', 'San Antonio')
        ])
        self.cmd('az monitor app-insights events show --start-time 2019-03-05 23:00:00 +00:00 --end-time 2019-03-05 23:05:00 +00:00 --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults', checks=[
            self.check('value[0].ai.appId', '578f0e27-12e9-4631-bc02-50b965da2633'),
        ])
        result = self.cmd('az monitor app-insights events show --start-time 2019-03-05 23:00:00 +00:00 --end-time 2019-03-05 23:05:00 +00:00 --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults').get_output_in_json()
        assert isinstance(result["value"][0]["client"]["city"], ("".__class__, u"".__class__))
        assert isinstance(result["value"][0]["availabilityResult"]["duration"], (int, float, complex))
