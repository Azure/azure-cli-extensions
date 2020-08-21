# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, StorageAccountPreparer


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
            'application_type': 'web',
            'retention_time': 120
        })

        self.cmd('az monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type} --retention-time {retention_time}', checks=[
            self.check('name', '{name_a}'),
            self.check('location', '{loc}'),
            self.check('kind', '{kind}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{name_a}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        self.cmd('monitor app-insights component billing show --app {name_a} -g {resource_group}', checks=[
            self.check("contains(keys(@), 'dataVolumeCap')", True)
        ])

        self.cmd('monitor app-insights component billing update --app {name_a} -g {resource_group} --cap 200.5 -s', checks=[
            self.check('dataVolumeCap.cap', 200.5),
            self.check('dataVolumeCap.stopSendNotificationWhenHitCap', True),
        ])

        self.kwargs.update({
            'kind': 'ios',
            'retention_time': 180
        })

        self.cmd('az monitor app-insights component update --app {name_a} --kind {kind} -g {resource_group} --retention-time {retention_time}', checks=[
            self.check('kind', '{kind}'),
            self.check('retentionInDays', self.kwargs['retention_time'])
        ])

        self.cmd('az monitor app-insights component create --app {name_b} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('name', '{name_b}'),
            self.check('provisioningState', 'Succeeded'),
        ])

        apps = self.cmd('az monitor app-insights component show -g {resource_group}').get_output_in_json()
        assert len(apps) == 2

        self.cmd('az monitor app-insights component show -g {resource_group} --app {name_b}', checks=[
            self.check('name', '{name_b}')
        ])

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
            'apiKeyC': 'emptyKey',
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

        api_key = self.cmd('az monitor app-insights api-key create --app {name} -g {resource_group} --api-key {apiKeyC} --write-properties ""').get_output_in_json()
        assert len(api_key['linkedReadProperties']) >= 2  # Some are not user configurable but will be added automatically
        assert len(api_key['linkedWriteProperties']) == 0

        api_keys = self.cmd('az monitor app-insights api-key show --app {name} -g {resource_group}').get_output_in_json()
        assert len(api_keys) == 3

        self.cmd('az monitor app-insights api-key delete --app {name} -g {resource_group} --api-key {apiKeyB}', checks=[
            self.check('name', '{apiKeyB}')
        ])
        return

    @ResourceGroupPreparer(parameter_name_for_location='location')
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2')
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2', parameter_name='storage_account_2')
    def test_component_with_linked_storage(self, resource_group, location, storage_account, storage_account_2):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'demoApp',
            'kind': 'web',
            'application_type': 'web',
            'storage_account': storage_account,
            'ws_1': self.create_random_name('clitest', 20),
            'storage_account_2': storage_account_2
        })
        self.cmd('monitor log-analytics workspace create -g {resource_group} -n {ws_1}')
        self.cmd(
            'monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --workspace {ws_1} --application-type {application_type}',
            checks=[
                self.check('name', '{name_a}'),
                self.check('location', '{loc}'),
                self.check('kind', '{kind}'),
                self.check('applicationType', '{application_type}'),
                self.check('applicationId', '{name_a}'),
                self.check('provisioningState', 'Succeeded'),
            ])

        output_json = self.cmd('monitor app-insights component linked-storage link --app {name_a} -g {resource_group} -s {storage_account}').get_output_in_json()
        assert self.kwargs['storage_account'] in output_json['linkedStorageAccount']
        output_json = self.cmd('monitor app-insights component linked-storage show --app {name_a} -g {resource_group}').get_output_in_json()
        assert self.kwargs['storage_account'] in output_json['linkedStorageAccount']
        output_json = self.cmd('monitor app-insights component linked-storage update --app {name_a} -g {resource_group} -s {storage_account_2}').get_output_in_json()
        assert self.kwargs['storage_account_2'] in output_json['linkedStorageAccount']
        self.cmd('monitor app-insights component linked-storage unlink --app {name_a} -g {resource_group}')
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('monitor app-insights component linked-storage show --app {name_a} -g {resource_group}')

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_component_with_linked_workspace(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'ws_1': self.create_random_name('clitest', 20),
            'ws_2': self.create_random_name('clitest', 20)
        })

        self.cmd('monitor log-analytics workspace create -g {resource_group} -n {ws_1}')
        self.cmd('monitor log-analytics workspace create -g {resource_group} -n {ws_2}')
        self.cmd(
            'monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}',
            checks=[
                self.check('name', '{name_a}'),
                self.check('location', '{loc}'),
                self.check('kind', '{kind}'),
                self.check('applicationType', '{application_type}'),
                self.check('applicationId', '{name_a}'),
                self.check('provisioningState', 'Succeeded'),
            ])

        self.kwargs.update({
            'kind': 'ios'
        })

        output_json = self.cmd('az monitor app-insights component update --app {name_a} --workspace {ws_1} -g {resource_group}').get_output_in_json()
        assert self.kwargs['ws_1'] in output_json['workspaceResourceId']
        output_json = self.cmd('az monitor app-insights component update --app {name_a} --workspace {ws_2} -g {resource_group}').get_output_in_json()
        assert self.kwargs['ws_2'] in output_json['workspaceResourceId']

        output_json = self.cmd('az monitor app-insights component update --app {name_a} --workspace {ws_1} --kind {kind} -g {resource_group}').get_output_in_json()
        assert self.kwargs['ws_1'] in output_json['workspaceResourceId']
        assert output_json['kind'] == self.kwargs['kind']
        output_json = self.cmd('az monitor app-insights component create --app {name_b} --workspace {ws_2} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}').get_output_in_json()
        assert self.kwargs['ws_2'] in output_json['workspaceResourceId']
        assert output_json['kind'] == self.kwargs['kind']
        output_json = self.cmd('az monitor app-insights component update --app {name_b} --kind {kind} -g {resource_group}').get_output_in_json()
        assert output_json['kind'] == self.kwargs['kind']

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_component_with_public_network_access(self, resource_group, location):
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'demoApp',
            'name_b': 'testApp',
            'kind': 'web',
            'application_type': 'web',
            'ws_1': self.create_random_name('clitest', 20),
            'ws_2': self.create_random_name('clitest', 20)
        })

        self.cmd('monitor log-analytics workspace create -g {resource_group} -n {ws_1}')
        self.cmd('monitor log-analytics workspace create -g {resource_group} -n {ws_2}')
        self.cmd(
            'monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}',
            checks=[
                self.check('name', '{name_a}'),
                self.check('location', '{loc}'),
                self.check('kind', '{kind}'),
                self.check('applicationType', '{application_type}'),
                self.check('applicationId', '{name_a}'),
                self.check('provisioningState', 'Succeeded'),
            ])

        output_json = self.cmd('az monitor app-insights component update --app {name_a} --query-access Enabled --ingestion-access Enabled -g {resource_group}').get_output_in_json()
        assert output_json['publicNetworkAccessForIngestion'] == 'Enabled'
        assert output_json['publicNetworkAccessForQuery'] == 'Enabled'
        output_json = self.cmd('az monitor app-insights component update --app {name_a} --workspace {ws_1} --query-access Disabled --ingestion-access Disabled -g {resource_group}').get_output_in_json()
        assert self.kwargs['ws_1'] in output_json['workspaceResourceId']
        assert output_json['publicNetworkAccessForIngestion'] == 'Disabled'
        assert output_json['publicNetworkAccessForQuery'] == 'Disabled'
        output_json = self.cmd('az monitor app-insights component create --app {name_b} --workspace {ws_2} --location {loc} --query-access Enabled --ingestion-access Disabled -g {resource_group} --application-type {application_type}').get_output_in_json()
        assert self.kwargs['ws_2'] in output_json['workspaceResourceId']
        assert output_json['publicNetworkAccessForIngestion'] == 'Disabled'
        assert output_json['publicNetworkAccessForQuery'] == 'Enabled'

        self.kwargs.update({
            'kind': 'ios'
        })

        self.cmd('az monitor app-insights component update --app {name_b} --kind {kind} -g {resource_group}', checks=[
            self.check('kind', '{kind}')
        ])
