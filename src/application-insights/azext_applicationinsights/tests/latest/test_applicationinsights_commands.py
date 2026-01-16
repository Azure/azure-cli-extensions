# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class ApplicationInsightsDataClientTests(ScenarioTest):
    """Test class for Application Insights data client."""
    @unittest.skip("ResourceNotAvailable")
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

    @unittest.skip("ResourceNotAvailable")
    def test_query_execute_with_different_offset(self):
        """Tests data plane query capabilities for Application Insights."""
        self.cmd('az monitor app-insights query --apps db709f0e-cb4e-4f43-ba80-05e10d6a4447 --analytics-query "availabilityResults | distinct name | order by name asc" --offset P3DT12H')
        self.cmd('az monitor app-insights query --apps db709f0e-cb4e-4f43-ba80-05e10d6a4447 --analytics-query "availabilityResults | distinct name | order by name asc" --offset 3d12h1m')

    @unittest.skip("ResourceNotAvailable")
    def test_metrics_show(self):
        self.cmd('az monitor app-insights metrics show --app 578f0e27-12e9-4631-bc02-50b965da2633 --metrics requests/duration --aggregation count sum --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00', checks=[
            self.check('value."requests/duration".count', 0),
            self.check('value."requests/duration".sum', 0)
        ])
        result = self.cmd('az monitor app-insights metrics show --app /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ace-test/providers/microsoft.insights/components/ace-test -m availabilityResults/count --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00').get_output_in_json()
        azure_result = self.cmd('az monitor app-insights metrics show --app 578f0e27-12e9-4631-bc02-50b965da2633 --metric availabilityResults/count --start-time 2019-03-06 00:31 +00:00 --end-time 2019-03-06 01:31 +00:00').get_output_in_json()
        assert isinstance(result["value"]["availabilityResults/count"]['sum'], (int, float, complex))
        assert result["value"]["availabilityResults/count"]['sum'] == azure_result["value"]["availabilityResults/count"]['sum']

    @unittest.skip("ResourceNotAvailable")
    def test_metrics_get_metadata(self):
        self.cmd('az monitor app-insights metrics get-metadata --app 578f0e27-12e9-4631-bc02-50b965da2633', checks=[
            self.check('dimensions."availabilityResult/location".displayName', 'Run location'),
            self.check('metrics."availabilityResults/availabilityPercentage".displayName', 'Availability'),
            self.check('metrics."users/count".supportedAggregations[0]', 'unique'),
            self.check('metrics."users/count".supportedGroupBy.all[0]', 'trace/severityLevel')
        ])

    @unittest.skip("ResourceNotAvailable")
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

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_query_execute_for_app(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'testApp1',
            'name_b': 'testApp2',
            'kind1': 'web',
            'kind2': 'ios',
            'application_type': 'web',
            'retention_time': 120
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind1} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind1}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        self.cmd('az monitor app-insights component create --app {name_b} --location {loc} --kind {kind2} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_b}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind2}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_b}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])
        app1_info = self.cmd('az monitor app-insights component show --app {name_a} -g {resource_group}').get_output_in_json()
        app2_info = self.cmd('az monitor app-insights component show --app {name_b} -g {resource_group}').get_output_in_json()
        self.kwargs.update({
            'app_id1': app1_info["appId"],
            'id1': app1_info["id"],
            'app_id2': app2_info["appId"],
            'id2': app1_info["id"],
        })

        self.cmd('az monitor app-insights query --apps {app_id1} {app_id2} --analytics-query "availabilityResults | distinct name | order by name asc"', checks=[
            self.check('tables[0].name', 'PrimaryResult'),
            self.check('tables[0].columns[0].name', 'name'),
            self.check('tables[0].columns[0].type', 'string'),
        ])
        query_guid = self.cmd('az monitor app-insights query --app {app_id1} --analytics-query "requests | getschema"').get_output_in_json()
        query_name_rg = self.cmd('az monitor app-insights query --apps {name_a} -g {resource_group} --analytics-query "requests | getschema"').get_output_in_json()
        query_azure_id = self.cmd('az monitor app-insights query --analytics-query "requests | getschema" --ids {id1}').get_output_in_json()
        assert query_guid == query_name_rg
        assert query_name_rg == query_azure_id
        # might change over time
        # assert len(query_guid['tables'][0]['rows']) == 38
        assert isinstance(query_guid['tables'][0]['rows'][0][1], (int, float, complex))

        self.cmd('az monitor app-insights component delete --app {name_a} -g {resource_group}',
                 checks=[self.is_empty()])
        self.cmd('az monitor app-insights component delete --app {name_b} -g {resource_group}',
                 checks=[self.is_empty()])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_metrics_show_for_app(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'testApp1',
            'kind1': 'web',
            'application_type': 'web',
            'retention_time': 120
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind1} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind1}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        app1_info = self.cmd('az monitor app-insights component show --app {name_a} -g {resource_group}').get_output_in_json()
        self.kwargs.update({
            'app_id1': app1_info["appId"],
            'id1': app1_info["id"],
        })
        self.cmd('az monitor app-insights metrics show --app {app_id1} --metrics requests/duration --aggregation count sum --start-time 2025-04-06 00:31 +00:00 --end-time 2025-04-16 01:31 +00:00', checks=[
            self.check('value."requests/duration".count', None),
            self.check('value."requests/duration".sum', None)
        ])
        result = self.cmd('az monitor app-insights metrics show --app {id1} -m availabilityResults/count --start-time 2025-04-06 00:31 +00:00 --end-time 2025-04-16 01:31 +00:00').get_output_in_json()
        azure_result = self.cmd('az monitor app-insights metrics show --app {app_id1} --metric availabilityResults/count --start-time 2025-04-06 00:31 +00:00 --end-time 2025-04-16 01:31 +00:00').get_output_in_json()
        assert result["value"] == azure_result["value"]

        self.cmd('az monitor app-insights component delete --app {name_a} -g {resource_group}',
                 checks=[self.is_empty()])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_metrics_get_metadata_for_app(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'testApp1',
            'kind1': 'web',
            'application_type': 'web',
            'retention_time': 120
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind1} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind1}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        app1_info = self.cmd('az monitor app-insights component show --app {name_a} -g {resource_group}').get_output_in_json()
        self.kwargs.update({
            'app_id1': app1_info["appId"],
            'id1': app1_info["id"],
        })
        self.cmd('az monitor app-insights metrics get-metadata --app {app_id1}', checks=[
            self.check('dimensions."availabilityResult/location".displayName', 'Run location'),
            self.check('metrics."availabilityResults/availabilityPercentage".displayName', 'Availability'),
            self.check('metrics."users/count".supportedAggregations[0]', 'unique'),
            self.check('metrics."users/count".supportedGroupBy.all[0]', 'trace/severityLevel')
        ])

        self.cmd('az monitor app-insights component delete --app {name_a} -g {resource_group}',
                 checks=[self.is_empty()])


    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_events_show_for_app(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'testApp1',
            'kind1': 'web',
            'application_type': 'web',
            'retention_time': 120
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind1} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind1}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        app1_info = self.cmd('az monitor app-insights component show --app {name_a} -g {resource_group}').get_output_in_json()
        self.kwargs.update({
            'app_id1': app1_info["appId"],
            'id1': app1_info["id"],
        })
        result = self.cmd('az monitor app-insights events show --app {app_id1} --type availabilityResults --start-time 2025-04-06 00:31 +00:00 --end-time 2025-04-16 01:31 +00:00').get_output_in_json()
        assert result["value"] == []
        assert result["@ai.messages"][0]["code"] == "AddedLimitToQuery" # might change over time
        assert isinstance(result["@odata.context"], str)

        self.cmd('az monitor app-insights component delete --app {name_a} -g {resource_group}',
                 checks=[self.is_empty()])