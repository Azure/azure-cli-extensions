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
        self.cmd('az monitor app-insights query --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --analytics-query "availabilityResults | summarize count() by bin(timestamp, 6h), name | order by name desc"', checks=[
            self.check('tables[0].rows[0][1]', 'microsoft'),
            self.check('tables[0].rows[-1][1]', 'google')
        ])
        query_result = self.cmd('az monitor app-insights query --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --analytics-query "requests | getschema"').get_output_in_json()
        assert len(query_result['tables'][0]['rows']) == 37
        assert isinstance(query_result['tables'][0]['rows'][0][1], (int, float, complex))

    def test_metrics_show(self):
        result = self.cmd('az monitor app-insights metrics show --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --metric-id availabilityResults/count').get_output_in_json()
        assert isinstance(result["value"]["availabilityResults/count"]['sum'], (int, float, complex))

    def test_metrics_get_metadata(self):
        self.cmd('az monitor app-insights metrics get-metadata --app-id 578f0e27-12e9-4631-bc02-50b965da2633', checks=[
            self.check('dimensions."availabilityResult/location".displayName', 'Run location'),
            self.check('metrics."availabilityResults/availabilityPercentage".displayName', 'Availability'),
            self.check('metrics."users/count".supportedAggregations[0]', 'unique'),
            self.check('metrics."users/count".supportedGroupBy.all[0]', 'trace/severityLevel')
        ])

    def test_events_show(self):
        self.cmd('az monitor app-insights events show --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --event-type availabilityResults --event-id 1f492e8f-de80-11e8-8fec-e18ec74f57af', checks=[
            self.check('value[0].ai.appId', '578f0e27-12e9-4631-bc02-50b965da2633'),
            self.check('value[0].availabilityResult.duration', 104),
            self.check('value[0].client.city', 'Boydton')
        ])

    def test_events_list(self):
        self.cmd('az monitor app-insights events list --timespan PT5M --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --event-type availabilityResults', checks=[
            self.check('value[0].ai.appId', '578f0e27-12e9-4631-bc02-50b965da2633'),
        ])
        result = self.cmd('az monitor app-insights events list --timespan PT5M --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --event-type availabilityResults').get_output_in_json()
        assert isinstance(result["value"][0]["client"]["city"], str)
        assert isinstance(result["value"][0]["availabilityResult"]["duration"], (int, float, complex))
