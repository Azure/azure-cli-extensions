# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, StorageAccountPreparer
from .recording_processors import StorageAccountSASReplacer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


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

        app_config = self.cmd('az monitor app-insights component show -g {resource_group} --app {ai_name}').get_output_in_json()

        app_insights_instrumentation_key = app_config['instrumentationKey']
        app_insights_connection_string = app_config['connectionString']

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
        self.cmd('az monitor app-insights component connect-webapp -g {resource_group} --app {ai_name} --web-app {webapp_name} --enable-profiler --enable-snapshot-debugger')

        # Check if the settings are updated correctly.
        self.cmd('az webapp config appsettings list -g {resource_group} -n {webapp_name}', checks=[
            self.check("[?name=='APPINSIGHTS_PROFILERFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_SNAPSHOTFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_INSTRUMENTATIONKEY']|[0].value", app_insights_instrumentation_key),
            self.check("[?name=='APPINSIGHTS_CONNECTIONSTRING']|[0].value", app_insights_connection_string)
        ])

    @ResourceGroupPreparer(name_prefix="webapp_cross_rg", parameter_name="resource_group", parameter_name_for_location="location")
    @ResourceGroupPreparer(name_prefix="webapp_cross_rg2", parameter_name="resource_group2", parameter_name_for_location="location2")
    def test_connect_webapp_cross_resource_group(self, resource_group, resource_group2, location, location2):
        # Create Application Insights.
        ai_name = self.create_random_name('clitestai', 24)
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'resource_group2': resource_group2,
            'ai_name': ai_name,
            'kind': 'web',
            'application_type': 'web'
        })

        self.cmd(
            'az monitor app-insights component create --app {ai_name} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}',
            checks=[
                self.check('location', '{loc}'),
                self.check('kind', '{kind}'),
                self.check('applicationType', '{application_type}'),
                self.check('applicationId', '{ai_name}'),
                self.check('provisioningState', 'Succeeded')
            ])

        app_insights_instrumentation_key = self.cmd('az monitor app-insights component show -g {resource_group} --app {ai_name}').get_output_in_json()['instrumentationKey']

        # Create web app.
        webapp_name = self.create_random_name('clitestwebapp', 24)
        plan = self.create_random_name('clitestplan', 24)
        self.kwargs.update({
            'plan': plan,
            'webapp_name': webapp_name
        })

        self.cmd('az appservice plan create -g {resource_group2} -n {plan}')
        self.kwargs["webapp_id"] = self.cmd('az webapp create -g {resource_group2} -n {webapp_name} --plan {plan}', checks=[
            self.check('state', 'Running'),
            self.check('name', webapp_name)
        ]).get_output_in_json()['id']

        # Connect AI to web app and update settings for web app.
        self.cmd(
            'az monitor app-insights component connect-webapp -g {resource_group} --app {ai_name} --web-app {webapp_id} --enable-profiler --enable-snapshot-debugger')

        # Check if the settings are updated correctly.
        self.cmd('az webapp config appsettings list -g {resource_group2} -n {webapp_name}', checks=[
            self.check("[?name=='APPINSIGHTS_PROFILERFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_SNAPSHOTFEATURE_VERSION']|[0].value", '1.0.0'),
            self.check("[?name=='APPINSIGHTS_INSTRUMENTATIONKEY']|[0].value", app_insights_instrumentation_key)
        ])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    @StorageAccountPreparer()
    def test_connect_function(self, resource_group, storage_account, location):
        # Create Application Insights.
        ai_name = self.create_random_name('clitestai', 24)
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'ai_name': ai_name,
            'kind': 'web',
            'application_type': 'web',
            'sa': storage_account
        })

        self.cmd('az monitor app-insights component create --app {ai_name} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('location', '{loc}'),
            self.check('kind', '{kind}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{ai_name}'),
            self.check('provisioningState', 'Succeeded')
        ])

        app_config = self.cmd('az monitor app-insights component show -g {resource_group} --app {ai_name}').get_output_in_json()

        app_insights_instrumentation_key = app_config['instrumentationKey']
        app_insights_conenction_string = app_config["connectionString"]

        # Create Azure function.
        function_name = self.create_random_name('clitestfunction', 24)
        plan = self.create_random_name('clitestplan', 24)
        self.kwargs.update({
            'plan': plan,
            'function_name': function_name
        })

        self.cmd('az appservice plan create -g {resource_group} -n {plan}')
        self.cmd('az functionapp create -g {resource_group} -n {function_name} --plan {plan} -s {sa} --functions-version 4 --runtime node', checks=[
            self.check('state', 'Running'),
            self.check('name', function_name)
        ])

        # Connect AI to function and update settings for function.
        self.cmd('az monitor app-insights component connect-function -g {resource_group} --app {ai_name} --function {function_name}')

        # Check if the settings are updated correctly.
        self.cmd('az webapp config appsettings list -g {resource_group} -n {function_name}', checks=[
            self.check("[?name=='APPINSIGHTS_INSTRUMENTATIONKEY']|[0].value", app_insights_instrumentation_key),
            self.check("[?name=='APPINSIGHTS_CONNECTIONSTRING']|[0].value", app_insights_conenction_string)
        ])

    @ResourceGroupPreparer(name_prefix="connect_function_cross_rg", parameter_name="resource_group", parameter_name_for_location="location")
    @ResourceGroupPreparer(name_prefix="connect_function_cross_rg2", parameter_name="resource_group2", parameter_name_for_location="location2")
    @StorageAccountPreparer(resource_group_parameter_name='resource_group2')
    def test_connect_function_cross_resource_groups(self, resource_group, resource_group2, location, location2, storage_account):
        # Create Application Insights.
        ai_name = self.create_random_name('clitestai', 24)
        self.kwargs.update({
            'loc': location,
            'resource_group': resource_group,
            'resource_group2': resource_group2,
            'ai_name': ai_name,
            'kind': 'web',
            'application_type': 'web',
            'sa': storage_account
        })

        self.cmd('az monitor app-insights component create --app {ai_name} --location {loc} --kind {kind} -g {resource_group} --application-type {application_type}', checks=[
            self.check('location', '{loc}'),
            self.check('kind', '{kind}'),
            self.check('applicationType', '{application_type}'),
            self.check('applicationId', '{ai_name}'),
            self.check('provisioningState', 'Succeeded')
        ])

        app_insights_instrumentation_key = self.cmd('az monitor app-insights component show -g {resource_group} --app {ai_name}').get_output_in_json()['instrumentationKey']

        # Create Azure function.
        function_name = self.create_random_name('clitestfunction', 24)
        plan = self.create_random_name('clitestplan', 24)
        self.kwargs.update({
            'plan': plan,
            'function_name': function_name
        })

        self.cmd('az appservice plan create -g {resource_group2} -n {plan}')
        self.kwargs['functionapp_id'] = self.cmd('az functionapp create -g {resource_group2} -n {function_name} --plan {plan} -s {sa} --functions-version 4 --runtime node', checks=[
            self.check('state', 'Running'),
            self.check('name', function_name)
        ]).get_output_in_json()['id']

        # Connect AI to function and update settings for function.
        self.cmd('az monitor app-insights component connect-function -g {resource_group} --app {ai_name} --function {functionapp_id}')

        # Check if the settings are updated correctly.
        self.cmd('az webapp config appsettings list -g {resource_group2} -n {function_name}', checks=[
            self.check("[?name=='APPINSIGHTS_INSTRUMENTATIONKEY']|[0].value", app_insights_instrumentation_key)
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
        assert len(api_key['linkedWriteProperties']) == 0

        api_key = self.cmd('az monitor app-insights api-key create --app {name} -g {resource_group} --api-key {apiKeyB}').get_output_in_json()
        assert (api_key['apiKey'] is not None)

        api_key = self.cmd('az monitor app-insights api-key create --app {name} -g {resource_group} --api-key {apiKeyC} --write-properties "WriteAnnotations"').get_output_in_json()
        assert len(api_key['linkedReadProperties']) >= 2  # Some are not user configurable but will be added automatically
        assert len(api_key['linkedWriteProperties']) == 1

        api_keys = self.cmd('az monitor app-insights api-key show --app {name} -g {resource_group}').get_output_in_json()
        assert len(api_keys) == 3

        self.cmd('az monitor app-insights api-key delete --app {name} -g {resource_group} --api-key {apiKeyB} -y', checks=[
            self.check('name', '{apiKeyB}')
        ])
        return

    @ResourceGroupPreparer(parameter_name_for_location='location')
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2')
    @StorageAccountPreparer(name_prefix='component', kind='StorageV2', parameter_name='storage_account_2')
    def test_component_with_linked_storage(self, resource_group, location, storage_account, storage_account_2):
        from azure.core.exceptions import ResourceNotFoundError
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
        self.cmd('monitor app-insights component linked-storage unlink --app {name_a} -g {resource_group} -y')
        with self.assertRaisesRegexp(ResourceNotFoundError, "Operation returned an invalid status 'Not Found'"):
            self.cmd('monitor app-insights component linked-storage show --app {name_a} -g {resource_group}')

    @AllowLargeResponse()
    @ResourceGroupPreparer(parameter_name_for_location='location')
    @StorageAccountPreparer(kind='StorageV2')
    @StorageAccountPreparer(kind='StorageV2', location='westus2', parameter_name='storage_account_2')
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
        self.cmd('storage container create -n {container_name_a} -g {resource_group} --account-name {account_name_a}')
        self.cmd('storage container create -n {container_name_b} -g {resource_group} --account-name {account_name_b}')
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

    @ResourceGroupPreparer(name_prefix="cli_test_appinsights_", location="westus")
    def test_appinsights_webtest_crud(self, resource_group_location):
        self.kwargs.update({
            "loc": resource_group_location,
            "app_name": "test-app",
            "name": "test-webtest",
            "kind": "standard",
            "location_id1": "us-fl-mia-edge",
            "location_id2": "apac-hk-hkn-azr",
            "http_verb": "POST",
            "request_body": "SGVsbG8gd29ybGQ=",
            "request_url": "https://www.bing.com"
        })

        # prepare hidden-link
        app_id = self.cmd("monitor app-insights component create -a {app_name} -l {loc} -g {rg} --kind web --application-type web").get_output_in_json()["id"]
        self.kwargs["tag"] = f"hidden-link:{app_id}"

        self.cmd(
            "monitor app-insights web-test create -n {name} -l {loc} -g {rg} "
            "--enabled true --frequency 900 --web-test-kind {kind} --locations Id={location_id1} --defined-web-test-name {name} "
            "--http-verb {http_verb} --request-body {request_body} --request-url {request_url} --retry-enabled true --synthetic-monitor-id {name} --timeout 120 "
            "--ssl-lifetime-check 100 --ssl-check true --tags {tag}=Resource",
            checks=[
                self.check("webTestName", "{name}"),
                self.check("type", "microsoft.insights/webtests")
            ]
        )
        self.cmd(
            "monitor app-insights web-test list -g {rg} --component-name {app_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].webTestName", "{name}")
            ]
        )
        self.cmd("monitor app-insights web-test update -n {name} -l {loc} -g {rg} --locations Id={location_id2}")
        self.cmd(
            "monitor app-insights web-test show -n {name} -g {rg}",
            checks=[
                self.check("locations[0].location", "{location_id2}"),
                self.check("webTestName", "{name}")
            ]
        )
        self.cmd("monitor app-insights web-test delete -n {name} -g {rg} --yes")

        self.cmd(
            "monitor app-insights web-test create -n {name} -l {loc} -g {rg} "
            "--enabled true --frequency 900 --web-test-kind {kind} --locations Id={location_id1} --defined-web-test-name {name} "
            "--http-verb {http_verb} --request-body {request_body} --request-url {request_url} --retry-enabled true --synthetic-monitor-id {name} --timeout 120 "
            "--ssl-lifetime-check 100 --ssl-check true --headers key=x-ms-test value=123 --tags {tag}=Resource",
            checks=[
                self.check("webTestName", "{name}"),
                self.check("type", "microsoft.insights/webtests")
            ]
        )
        self.cmd(
            "monitor app-insights web-test list -g {rg} --component-name {app_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].webTestName", "{name}")
            ]
        )

    @ResourceGroupPreparer(name_prefix="cli_test_appinsights_component_favorite_")
    def test_appinsights_component_favorite(self, resource_group):
        self.kwargs.update({
            'app_name': self.create_random_name('app', 10),
            'favorite_name': self.create_random_name('favorite', 15)
        })
        self.cmd('monitor app-insights component create --app {app_name} --kind web -g {rg} --application-type web --retention-time 120 -l eastus')
        self.cmd('monitor app-insights component favorite create -g {rg} -n {favorite_name} --resource-name {app_name} --config myconfig --version ME --favorite-id {favorite_name} --favorite-type shared', checks=[
            self.check('Config', 'myconfig'),
            self.check('FavoriteId', '{favorite_name}'),
            self.check('FavoriteType', 'shared'),
            self.check('Name', '{favorite_name}'),
            self.check('Version', 'ME')
        ])
        self.cmd('monitor app-insights component favorite update -g {rg} -n {favorite_name} --resource-name {app_name} --config myconfig --version ME --favorite-id {favorite_name} --favorite-type shared --tags [tag,test]', checks=[
            self.check('Config', 'myconfig'),
            self.check('FavoriteId', '{favorite_name}'),
            self.check('FavoriteType', 'shared'),
            self.check('Name', '{favorite_name}'),
            self.check('Version', 'ME'),
            self.check('Tags', ['tag', 'test'])
        ])
        self.cmd('monitor app-insights component favorite show -g {rg} -n {favorite_name} --resource-name {app_name}', checks=[
            self.check('Config', 'myconfig'),
            self.check('FavoriteId', '{favorite_name}'),
            self.check('FavoriteType', 'shared'),
            self.check('Name', '{favorite_name}'),
            self.check('Version', 'ME'),
            self.check('Tags', ['tag', 'test'])
        ])
        self.cmd('monitor app-insights component favorite list -g {rg} --resource-name {app_name} --favorite-type shared --tags [tag]', checks=[
            self.check('[0].Config', 'myconfig'),
            self.check('[0].FavoriteId', '{favorite_name}'),
            self.check('[0].FavoriteType', 'shared'),
            self.check('[0].Name', '{favorite_name}'),
            self.check('[0].Version', 'ME'),
            self.check('[0].Tags', ['tag', 'test'])
        ])
        self.cmd('monitor app-insights component favorite delete -g {rg} -n {favorite_name} --resource-name {app_name} -y')

    @ResourceGroupPreparer(name_prefix="cli_test_appinsights_my_workbook")
    def test_appinsights_my_workbook(self, resource_group):
        from azure.core.exceptions import ResourceNotFoundError
        message = "Resource type 'myWorkbooks' of provider namespace 'Microsoft.Insights' was not found in global location for api version '2021-03-08'."
        with self.assertRaisesRegex(ResourceNotFoundError, message):
            self.cmd('monitor app-insights my-workbook list -g {rg} --category performance')

    @ResourceGroupPreparer(name_prefix="cli_test_appinsights_workbook")
    def test_appinsights_workbook(self, resource_group):
        self.kwargs.update({
            'workbook_name': self.create_random_name('workbook', 15)
        })
        self.cmd('monitor app-insights workbook create -g {rg} --display-name {workbook_name} -n 00000000-0000-0000-0000-000000000000 --category workbook --serialized-data mydata --kind shared', checks=[
            self.check('category', 'workbook'),
            self.check('displayName', '{workbook_name}'),
            self.check('kind', 'shared'),
            self.check('name', '00000000-0000-0000-0000-000000000000'),
            self.check('serializedData', 'mydata')
        ])
        self.cmd('monitor app-insights workbook update -g {rg} -n 00000000-0000-0000-0000-000000000000 --tags {{tag:test}}', checks=[
            self.check('category', 'workbook'),
            self.check('displayName', '{workbook_name}'),
            self.check('kind', 'shared'),
            self.check('name', '00000000-0000-0000-0000-000000000000'),
            self.check('tags.tag', 'test')
        ])
        self.cmd('monitor app-insights workbook show -g {rg} -n 00000000-0000-0000-0000-000000000000', checks=[
            self.check('category', 'workbook'),
            self.check('displayName', '{workbook_name}'),
            self.check('kind', 'shared'),
            self.check('name', '00000000-0000-0000-0000-000000000000'),
            self.check('tags.tag', 'test')
        ])
        self.cmd('monitor app-insights workbook list -g {rg} --category workbook', checks=[
            self.check('[0].category', 'workbook'),
            self.check('[0].displayName', '{workbook_name}'),
            self.check('[0].kind', 'shared'),
            self.check('[0].name', '00000000-0000-0000-0000-000000000000'),
            self.check('[0].tags.tag', 'test')
        ])
        self.cmd('monitor app-insights workbook delete -g {rg} -n 00000000-0000-0000-0000-000000000000 -y')

    @ResourceGroupPreparer(name_prefix="cli_test_appinsights_workbook_identity")
    def test_appinsights_workbook_identity(self, resource_group):
        self.kwargs.update({
            'workbook_name': self.create_random_name('workbook', 15),
            'workbook_name2': self.create_random_name('workbook', 15),
            'identity1': self.create_random_name('id', 10),
            'identity2': self.create_random_name('id', 10)
        })
        identity1 = self.cmd('identity create --name {identity1} -g {rg}').get_output_in_json()
        identity2 = self.cmd('identity create --name {identity2} -g {rg}').get_output_in_json()
        self.kwargs.update({
            'id1': identity1['id'],
            'id2': identity2['id']
        })
        self.cmd('monitor app-insights workbook create -g {rg} --display-name {workbook_name} -n 00000000-0000-0000-0000-000000000000 --category workbook --kind shared --mi-user-assigned {id1}', checks=[
            self.check('category', 'workbook'),
            self.check('displayName', '{workbook_name}'),
            self.check('kind', 'shared'),
            self.check('name', '00000000-0000-0000-0000-000000000000'),
            self.check('identity.type', 'UserAssigned'),
            self.check('identity.userAssignedIdentities', {identity1['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity assign -g {rg} -n 00000000-0000-0000-0000-000000000000 --user-assigned {id2}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('userAssignedIdentities', {identity1['id']: {}, identity2['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity remove -g {rg} -n 00000000-0000-0000-0000-000000000000 --user-assigned {id1}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('userAssignedIdentities', {identity2['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity remove -g {rg} -n 00000000-0000-0000-0000-000000000000 --user-assigned {id2}', checks=[
            self.check('type', None)
        ])

        self.cmd('monitor app-insights workbook create -g {rg} --display-name {workbook_name2} -n 00000000-0000-0000-0000-000000000001 --category workbook --kind shared', checks=[
            self.check('category', 'workbook'),
            self.check('displayName', '{workbook_name2}'),
            self.check('kind', 'shared'),
            self.check('name', '00000000-0000-0000-0000-000000000001')
        ])
        self.cmd('monitor app-insights workbook identity assign -g {rg} -n 00000000-0000-0000-0000-000000000001 --user-assigned {id1}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('userAssignedIdentities', {identity1['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity assign -g {rg} -n 00000000-0000-0000-0000-000000000001 --user-assigned {id2}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('userAssignedIdentities', {identity1['id']: {}, identity2['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity remove -g {rg} -n 00000000-0000-0000-0000-000000000001 --user-assigned {id1}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('userAssignedIdentities', {identity2['id']: {}})
        ])
        self.cmd('monitor app-insights workbook identity remove -g {rg} -n 00000000-0000-0000-0000-000000000001 --user-assigned {id2}', checks=[
            self.check('type', None)
        ])
