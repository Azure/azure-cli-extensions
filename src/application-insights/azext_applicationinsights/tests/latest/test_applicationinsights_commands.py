# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class ApplicationInsightsDataClientTests(ScenarioTest):
    """Test class for Application Insights data client."""

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_query_execute(self, resource_group, location):
        """Tests data plane query capabilities for Application Insights."""
        self.kwargs.update({
            'loc': location,
            'rg': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'retention_time': 120
        })
        pr = self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {rg} --application-type {application_type} --retention-time {retention_time}').get_output_in_json()
        self.kwargs['app_id'] = pr['appId']
        self.kwargs['Resource_id'] = pr['id']

        self.cmd('az monitor app-insights query --apps {app_id} --analytics-query "availabilityResults | distinct name | order by name asc"', checks=[
            self.check('tables[0].rows[-1][0]', None),
            self.check('tables[0].rows[-2][0]', None)
        ])
        query_guid = self.cmd('az monitor app-insights query --app {app_id} --analytics-query "requests | getschema"').get_output_in_json()
        query_name_rg = self.cmd('az monitor app-insights query --apps demoApp -g {rg} --analytics-query "requests | getschema"').get_output_in_json()
        query_azure_id = self.cmd('az monitor app-insights query --analytics-query "requests | getschema" --ids {Resource_id} -g {rg}').get_output_in_json()
        assert query_guid == query_name_rg
        assert query_name_rg == query_azure_id
        assert len(query_guid['tables'][0]['rows']) == 37
        assert isinstance(query_guid['tables'][0]['rows'][0][1], (int, float, complex))

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_query_execute_with_different_offset(self,resource_group, location):
        """Tests data plane query capabilities for Application Insights."""
        self.kwargs.update({
            'loc': location,
            'rg': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'retention_time': 120
        })
        pr = self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {rg} --application-type {application_type} --retention-time {retention_time}').get_output_in_json()
        self.kwargs['app_id'] = pr['appId']
        self.cmd('az monitor app-insights query --apps {app_id} --analytics-query "availabilityResults | distinct name | order by name asc" --offset P3DT12H')
        self.cmd('az monitor app-insights query --apps {app_id} --analytics-query "availabilityResults | distinct name | order by name asc" --offset 3d12h1m')

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_metrics_show(self,resource_group, location):
        self.kwargs.update({
            'loc': location,
            'rg': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'retention_time': 120
        })
        pr = self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {rg} --application-type {application_type} --retention-time {retention_time}').get_output_in_json()
        self.kwargs['app_id'] = pr['appId']
        self.kwargs['Resource_id'] = pr['id']
        self.cmd('az monitor app-insights metrics show --app {app_id} --metrics requests/duration --aggregation count sum', checks=[
            self.check('value."requests/duration".count', None),
            self.check('value."requests/duration".sum', None)
        ])
        result = self.cmd('az monitor app-insights metrics show --app {Resource_id} -g {rg} -m availabilityResults/count').get_output_in_json()
        azure_result = self.cmd('az monitor app-insights metrics show --app {app_id} --metric availabilityResults/count').get_output_in_json()
        self.check(result["value"]["availabilityResults/count"]['sum'], None)
        assert result["value"]["availabilityResults/count"]['sum'] == azure_result["value"]["availabilityResults/count"]['sum']

    @unittest.skip('We have to skip this as there are some issue with SDK')
    def test_metrics_get_metadata(self):
        self.cmd('az monitor app-insights metrics get-metadata --app fbed6140-d053-4dd5-9c42-b26e7904e442', checks=[
            self.check('dimensions."availabilityResult/location".displayName', 'Run location'),
            self.check('metrics."availabilityResults/availabilityPercentage".displayName', 'Availability'),
            self.check('metrics."users/count".supportedAggregations[0]', 'unique'),
            self.check('metrics."users/count".supportedGroupBy.all[0]', 'trace/severityLevel')
        ])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_events_show(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'rg': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'retention_time': 120
        })
        pr = self.cmd( 'az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {rg} --application-type {application_type} --retention-time {retention_time}').get_output_in_json()
        self.kwargs['app_id'] = pr['appId']
        self.cmd('az monitor app-insights events show --app {app_id} --type availabilityResults --offset 24h --event 792aeac4-3f9a-11e9-bbeb-376e4a601afa', checks=[
            self.check('value[0].ai.appId', None),
            self.check('value[0].availabilityResult.duration', None),
            self.check('value[0].client.city', None)
        ])
        self.cmd('az monitor app-insights events show --start-time 2019-03-05 23:00:00 +00:00 --end-time 2019-03-05 23:05:00 +00:00 --app fbed6140-d053-4dd5-9c42-b26e7904e442 --type availabilityResults', checks=[
            self.check('value[0].ai.appId', None)
        ])
       # result = self.cmd('az monitor app-insights events show --start-time 2019-03-05 23:00:00 +00:00 --end-time 2019-03-05 23:05:00 +00:00 --app fbed6140-d053-4dd5-9c42-b26e7904e442 --type availabilityResults').get_output_in_json()
       # assert isinstance(result["value"][0]["client"]["city"], ("".__class__, u"".__class__))
       # assert isinstance(result["value"][0]["availabilityResult"]["duration"], (int, float, complex))
