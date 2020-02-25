# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest


class ApplicationInsightsManagementClientTests(ScenarioTest):
    """Test class for ApplicationInsights mgmt cli."""
    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_component(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web'
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('monitor app-insights component billing show --app {name_a} -g {resource_group}', checks=[
            self.check("contains(keys(@), 'dataVolumeCap')", True)
        ])

        self.cmd('monitor app-insights component billing update --app {name_a} -g {resource_group} --cap 200 -s', checks=[
            self.check('dataVolumeCap.cap', 200),
            self.check('dataVolumeCap.stopSendNotificationWhenHitCap', True),
        ])

        self.kwargs.update({
            'kind': 'ios'
        })

        self.cmd('az monitor app-insights component update --app {name_a} --kind {kind} -g {resource_group}', checks=[
            self.check('kind', '{kind}')
        ])

        self.cmd('az monitor app-insights component create --app {name_b} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('name', '{name_b}'),
            self.check('provisioningState', 'Succeeded'),
        ])

        apps = self.cmd('az monitor app-insights component show -g {resource_group}').get_output_in_json()
        assert len(apps) == 2

        self.cmd('az monitor app-insights component delete --app {name_a} -g {resource_group}', checks=[self.is_empty()])
        return

    """Test class for ApplicationInsights mgmt cli."""
    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_api_key(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name': 'demoApp',
            'apiKey': 'demoKey',
            'apiKeyB': 'otherKey',
            'kind': 'web',
            'application_type': 'web'
        })

        self.cmd('az monitor app-insights component create --app {name} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}')
        self.cmd('az monitor app-insights api-key create --app {name} -g {resource_group} --api-key {apiKey}', checks=[
            self.check('name', '{apiKey}'),
            self.check('resourceGroup', '{resource_group}')
        ])

        api_key = self.cmd('az monitor app-insights api-key show --app {name} -g {resource_group} --api-key {apiKey}').get_output_in_json()
        assert len(api_key['linkedReadProperties']) >= 2  # Some are not user configurable but will be added automatically
        assert len(api_key['linkedWriteProperties']) == 1

        api_key = self.cmd('az monitor app-insights api-key create --app {name} -g {resource_group} --api-key {apiKeyB}').get_output_in_json()
        assert (api_key['apiKey'] is not None)

        api_keys = self.cmd('az monitor app-insights api-key show --app {name} -g {resource_group}').get_output_in_json()
        assert len(api_keys) == 2

        self.cmd('az monitor app-insights api-key delete --app {name} -g {resource_group} --api-key {apiKeyB}', checks=[
            self.check('name', '{apiKeyB}')
        ])
        return
