# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class TimeSeriesInsightsClientScenarioTest(ScenarioTest):

    def _create_timeseriesinsights_environment(self):
        self.kwargs.update({
            'env': self.create_random_name('cli-test-tsi-env', 24),
        })
        # Create an environment with the name of {env}. Similar to
        # https://github.com/Azure/azure-cli/blob/31a9724478c67751ae0bee6cc0d9b75b763df17c/src/azure-cli/azure/cli/command_modules/keyvault/tests/latest/test_keyvault_commands.py#L34
        return self.cmd('az timeseriesinsights environment standard create '
                        '--resource-group {rg} '
                        '--name {env} '
                        '--sku-name S1 '
                        '--sku-capacity 1 '
                        '--data-retention-time 31 '
                        '--partition-key-properties DeviceId1 '
                        '--storage-limit-exceeded-behavior PauseIngress')

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    def test_timeseriesinsights_environment_standard(self, resource_group):
        self.kwargs.update({
            'env': self.create_random_name('cli-test-tsi-env', 24),
        })

        # Test environment standard create
        self.cmd('az timeseriesinsights environment standard create '
                 '--resource-group {rg} '
                 '--name {env} '
                 '--sku-name S1 '
                 '--sku-capacity 1 '
                 '--data-retention-time 7 '
                 '--partition-key-properties DeviceId1 '
                 '--storage-limit-exceeded-behavior PauseIngress',
                 checks=[self.check('name', '{env}')])

        self.cmd('az timeseriesinsights environment standard update --resource-group {rg} --name {env} --sku-name S1 --sku-capacity 2',
                 checks=[self.check('sku.capacity', '2')])

        self.cmd('az timeseriesinsights environment standard update --resource-group {rg} --name {env} --data-retention-time 8',
                 checks=[self.check('dataRetentionTime', '8 days, 0:00:00')])

        self.cmd('az timeseriesinsights environment standard update --resource-group {rg} --name {env} --storage-limit-exceeded-behavior PurgeOldData',
                 checks=[self.check('storageLimitExceededBehavior', 'PurgeOldData')])

        self.cmd('az timeseriesinsights environment show '
                 '--resource-group {rg} '
                 '--name {env}',
                 checks=[self.check('name', '{env}')])

        self.cmd('az timeseriesinsights environment list '
                 '--resource-group {rg}',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az timeseriesinsights environment list',
                 checks=[self.check("length([?name=='{env}'])", 1)])

        self.cmd('az timeseriesinsights environment delete '
                 '--resource-group {rg} '
                 '--name {env} --yes',
                 checks=[])

        self.cmd('az timeseriesinsights environment list '
                 '--resource-group {rg}',
                 checks=[self.check('length(@)', 0)])

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    @StorageAccountPreparer()
    def test_timeseriesinsights_environment_longterm(self, resource_group, storage_account):

        self.kwargs.update({
            'env': self.create_random_name('cli-test-tsi-env', 24),
        })

        # Test environment longterm create
        key = self.cmd('az storage account keys list -g {rg} -n {sa}  --query "[0].value" --output tsv').output

        self.cmd('az timeseriesinsights environment longterm create '
                 '--resource-group {rg} '
                 '--name {env} '
                 '--sku-name L1 '
                 '--sku-capacity 1 '
                 '--data-retention 7 '
                 '--time-series-id-properties DeviceId1 '
                 '--storage-account-name {sa} '
                 '--storage-management-key ' + key,
                 checks=[self.check('name', '{env}'),
                         self.check('timeSeriesIdProperties[0].name', 'DeviceId1')])

        self.cmd('az timeseriesinsights environment longterm update --resource-group {rg} --name {env} --data-retention 8',
                 checks=[self.check('dataRetention', '8 days, 0:00:00')])

        time.sleep(60)
        key = self.cmd('az storage account keys renew -g {rg} -n {sa} --key primary  --query "[0].value" --output tsv').output
        time.sleep(15)
        self.cmd('az timeseriesinsights environment longterm update --resource-group {rg} --name {env} --storage-management-key ' + key,
                 checks=[])

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    def test_timeseriesinsights_event_source_eventhub(self, resource_group):
        self.kwargs.update({
            'es': self.create_random_name('cli-test-tsi-es', 24),  # time series insights event source
            'ehns': self.create_random_name('cli-test-tsi-ehns', 24),  # event hub namespace
            'eh': self.create_random_name('cli-test-tsi-eh', 24),  # event hub
            'loc': 'westus'
        })

        self._create_timeseriesinsights_environment()

        # Create

        # Prepare the event hub
        self.cmd('az eventhubs namespace create -g {rg} -n {ehns}')
        result = self.cmd('az eventhubs eventhub create -g {rg} -n {eh} --namespace-name {ehns}').get_output_in_json()
        self.kwargs["es_resource_id"] = result["id"]
        result = self.cmd('az eventhubs namespace authorization-rule keys list -g {rg} --namespace-name {ehns} -n RootManageSharedAccessKey').get_output_in_json()
        self.kwargs["shared_access_key"] = result["primaryKey"]

        # Test --timestamp-property-name is not given
        self.cmd('az timeseriesinsights event-source eventhub create -g {rg} --environment-name {env} --name {es} '
                 '--key-name RootManageSharedAccessKey '
                 '--shared-access-key {shared_access_key} '
                 '--event-source-resource-id {es_resource_id} '
                 '--consumer-group-name $Default',
                 checks=[self.check('timestampPropertyName', None)])

        self.cmd('az timeseriesinsights event-source eventhub create -g {rg} --environment-name {env} --name {es} '
                 '--key-name RootManageSharedAccessKey '
                 '--shared-access-key {shared_access_key} '
                 '--event-source-resource-id {es_resource_id} '
                 '--consumer-group-name $Default --timestamp-property-name timestampProp',
                 checks=[self.check('timestampPropertyName', 'timestampProp')])

        self.cmd('az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} --name {es} '
                 '--timestamp-property-name DeviceId1')

        # Currently only Embedded is supported
        self.cmd('az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} --name {es} '
                 '--local-timestamp-format Embedded')

        # Iana, TimeSpan
        # self.cmd('az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} --name {es} '
        #          '--local-timestamp-format Timespan --time-zone-offset-property-name Offset')

        # Renew a key
        self.kwargs["shared_access_key"] = self.cmd('az eventhubs namespace authorization-rule keys renew -g {rg} --namespace-name {ehns} -n RootManageSharedAccessKey --key PrimaryKey --query primaryKey --output tsv').output

        self.cmd('az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} --name {es} --shared-access-key {shared_access_key}')

        # List
        self.cmd('az timeseriesinsights event-source list -g {rg} --environment-name {env}',
                 checks=[self.check('length(@)', 1)])

        # Show
        self.cmd('az timeseriesinsights event-source show -g {rg} --environment-name {env} -n {es}')

        # Delete
        self.cmd('az timeseriesinsights event-source delete -g {rg} --environment-name {env} -n {es} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    def test_timeseriesinsights_event_source_iothub(self):
        self.kwargs.update({
            'es': self.create_random_name('cli-test-tsi-es', 24),  # time series insights event source
            'iothub': self.create_random_name('cli-test-tsi-iothub', 24),  # iot hub
            'loc': 'westus'
        })

        self._create_timeseriesinsights_environment()

        # Create
        # Prepare the iot hub
        result = self.cmd('az iot hub create -g {rg} -n {iothub}').get_output_in_json()
        self.kwargs["es_resource_id"] = result["id"]
        self.kwargs["key_name"] = "iothubowner"
        self.kwargs["shared_access_key"] = self.cmd("az iot hub policy list -g {rg} --hub-name {iothub} --query \"[?keyName=='iothubowner']\".primaryKey --output tsv").output

        # Test --timestamp-property-name is not given
        self.cmd('az timeseriesinsights event-source iothub create -g {rg} --environment-name {env} --name {es} '
                 '--consumer-group-name $Default '
                 '--key-name {key_name} --shared-access-key {shared_access_key} '
                 '--event-source-resource-id {es_resource_id}',
                 checks=[self.check('timestampPropertyName', None)])

        self.cmd('az timeseriesinsights event-source iothub create -g {rg} --environment-name {env} --name {es} '
                 '--consumer-group-name $Default '
                 '--key-name {key_name} --shared-access-key {shared_access_key} '
                 '--event-source-resource-id {es_resource_id} --timestamp-property-name timestampProp',
                 checks=[self.check('timestampPropertyName', 'timestampProp')])

        self.cmd('az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} --name {es} '
                 '--timestamp-property-name DeviceId1')

        # Currently only Embedded is supported
        self.cmd('az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} --name {es} '
                 '--local-timestamp-format Embedded')

        # Iana, TimeSpan
        # self.cmd('az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} --name {es} '
        #          '--local-timestamp-format Timespan --time-zone-offset-property-name Offset')

        self.kwargs["shared_access_key"] = self.cmd('az iot hub policy renew-key -g {rg} --hub-name {iothub} -n {key_name} --renew-key primary --query primaryKey --output tsv').output

        self.cmd('az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} --name {es} '
                 '--shared-access-key {shared_access_key}')

        # List
        self.cmd('az timeseriesinsights event-source list -g {rg} --environment-name {env}',
                 checks=[self.check('length(@)', 1)])

        # Show
        self.cmd('az timeseriesinsights event-source show -g {rg} --environment-name {env} -n {es}')

        # Delete
        self.cmd('az timeseriesinsights event-source delete -g {rg} --environment-name {env} -n {es} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    def test_timeseriesinsights_reference_data_set(self):
        self.kwargs.update({
            'rds': self.create_random_name('clitesttsirds', 24),  # time series insights event source
        })

        self._create_timeseriesinsights_environment()

        # Create
        self.cmd('az timeseriesinsights reference-data-set create -g {rg} --environment-name {env} --name {rds} '
                 '--key-properties DeviceId1 String DeviceFloor Double --data-string-comparison-behavior Ordinal')

        # Update
        self.cmd('az timeseriesinsights reference-data-set update -g {rg} --environment-name {env} --name {rds} '
                 '--tags mykey=myvalue')

        # List
        self.cmd('az timeseriesinsights reference-data-set list -g {rg} --environment-name {env}',
                 checks=[self.check('length(@)', 1)])

        # Show
        self.cmd('az timeseriesinsights reference-data-set show -g {rg} --environment-name {env} -n {rds}')

        # Delete
        self.cmd('az timeseriesinsights reference-data-set delete -g {rg} --environment-name {env} -n {rds} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_timeseriesinsights')
    def test_timeseriesinsights_access_policy(self):
        self.kwargs.update({
        })

        self._create_timeseriesinsights_environment()

        # Create
        self.cmd('az timeseriesinsights access-policy create -g {rg} --environment-name {env} --name ap1 --principal-object-id 001 --description "some description" --roles Contributor Reader',
                 checks=[])

        # Update
        self.cmd('az timeseriesinsights access-policy update -g {rg} --environment-name {env} --name ap1 --description "some description updated"',
                 checks=[])

        self.cmd('az timeseriesinsights access-policy update -g {rg} --environment-name {env} --name ap1 --roles Contributor',
                 checks=[])

        # Show
        self.cmd('az timeseriesinsights access-policy show -g {rg} --environment-name {env} --name ap1',
                 checks=[])
        # List
        self.cmd('az timeseriesinsights access-policy list -g {rg} --environment-name {env}',
                 checks=[self.check('length(@)', 1)])

        # Delete
        self.cmd('az timeseriesinsights access-policy delete -g {rg} --environment-name {env} --name ap1 --yes',
                 checks=[])
