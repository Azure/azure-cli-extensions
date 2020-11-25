# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, StorageAccountPreparer
from .recording_processors import StorageAccountSASReplacer


class ApplicationInsightsManagementClientTests(ScenarioTest):

    def __init__(self, method_name):
        self.sas_replacer = StorageAccountSASReplacer()
        super(ApplicationInsightsManagementClientTests, self).__init__(method_name, recording_processors=[
            self.sas_replacer
        ])

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

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_connect_webapp(self, resource_group, location):
        # Create Application Insights.
        ai_name = self.create_random_name('clitestai', 24)
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'ai_name': ai_name,
            'kind': 'web',
            'application_type': 'web'
        })

        self.cmd('az monitor app-insights component create --app {ai_name} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('location', '{loc}'),
            self.check('kind', '{kind}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{ai_name}'),
            self.check('provisioningState', 'Succeeded')
        ])

        # Create web app.
        webapp_name = self.create_random_name('clitestwebapp', 24)
        plan = self.create_random_name('clitestplan', 24)
        self.kwargs.update({
            'plan': plan,
            'webapp_name': webapp_name
        })

        self.cmd('az appservice plan create -g {resource_group} -n {plan}')
        self.cmd('az webapp create -g {resource_group} -n {webapp_name} --plan {plan}', checks=[
            self.check('state', 'Running'),
            self.check('name', webapp_name)
        ])

        # Connect AI to web app and update settings for web app.
        self.cmd('az monitor app-insights component connect-webapp -g {resource_group} -n {webapp_name} --enable-profiler --enable-snapshot-debugger', checks=[
            self.check("[?name=='APPINSIGHTS_PROFILERFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_SNAPSHOTFEATURE_VERSION']|[0].value", '1.0.0')
        ])

        # Check if the settings are updated correctly.
        self.cmd('az webapp config appsettings list -g {resource_group} -n {webapp_name}', checks=[
            self.check("[?name=='APPINSIGHTS_PROFILERFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_SNAPSHOTFEATURE_VERSION']|[0].value", '1.0.0')
        ])

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
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2')
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2', location='westus2', parameter_name='storage_account_2')
    def test_component_continues_export(self, resource_group, location, storage_account, storage_account_2):
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%MZ')
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'name_a': 'demoApp',
            'kind': 'web',
            'record_types_a': 'Requests Event Exceptions Metrics PageViews',
            'record_types_b': 'Requests Event PageViews',
            'account_name_a': storage_account,
            'account_name_b': storage_account_2,
            'container_name_a': 'ctna',
            'container_name_b': 'ctnb',
            'application_type': 'web',
            'expiry': expiry,
            'retention_time': 120
        })
        self.kwargs['dest_sub_id'] = self.cmd('account show').get_output_in_json()['id']
        self.cmd('storage container create -n {container_name_a} --account-name {account_name_a}')
        self.cmd('storage container create -n {container_name_b} --account-name {account_name_b}')
        self.kwargs['dest_sas_a'] = self.cmd('storage container generate-sas --account-name {account_name_a} --name {container_name_a} --permissions w --expiry {expiry}').output.replace('"', '').strip()
        self.kwargs['dest_sas_b'] = self.cmd('storage container generate-sas --account-name {account_name_b} --name {container_name_b} --permissions w --expiry {expiry}').output.replace('"', '').strip()
        self.sas_replacer.add_sas_token(self.kwargs['dest_sas_a'])
        self.sas_replacer.add_sas_token(self.kwargs['dest_sas_b'])
        self.cmd('monitor app-insights component create --app {name_a} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type} --retention-time {retention_time}').get_output_in_json()
        self.kwargs['export_id'] = self.cmd('monitor app-insights component continues-export create -g {resource_group} --app {name_a} --record-types {record_types_a} --dest-account {account_name_a} --dest-container {container_name_a} --dest-sub-id {dest_sub_id} --dest-sas {dest_sas_a}',
                                            checks=[
                                                self.check('@[0].storageName', self.kwargs['account_name_a']),
                                                self.check('@[0].containerName', self.kwargs['container_name_a'])
                                            ]).get_output_in_json()[0]['exportId']
        self.cmd('monitor app-insights component continues-export show -g {resource_group} --app {name_a} --id {export_id}',
                 checks=[
                     self.check('storageName', self.kwargs['account_name_a']),
                     self.check('containerName', self.kwargs['container_name_a'])
                 ])
        self.cmd('monitor app-insights component continues-export update -g {resource_group} --app {name_a} --id {export_id} --record-types {record_types_b} --dest-account {account_name_b} --dest-container {container_name_b} --dest-sub-id {dest_sub_id} --dest-sas {dest_sas_b}',
                 checks=[
                     self.check('storageName', self.kwargs['account_name_b']),
                     self.check('containerName', self.kwargs['container_name_b'])
                 ])
        self.cmd('monitor app-insights component continues-export list -g {resource_group} --app {name_a}',
                 checks=[
                     self.check('length(@)', 1)
                 ])
        self.cmd('monitor app-insights component continues-export delete -y -g {resource_group} --app {name_a} --id {export_id}')

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
