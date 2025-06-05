from azure.cli.testsdk import (
    ScenarioTest, record_only)
from azure.cli.testsdk.preparers import get_dummy_cli

class ConnectionAndFlowOperations(ScenarioTest):
    '''
    @ResourceGroupPreparer(name_prefix='testRg', location='westcentralus')
    @StorageAccountPreparer(name_prefix='shsengarcoupler', location='westcentralus')
    @StorageContainerPreparer(name_prefix='shsengarcouplercontainer')
    '''
    def test_connection_flow_operations(self):
        self.cli_ctx = get_dummy_cli()
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'sendConnection': self.create_random_name(prefix='test-send-connection-', length=30),
            'receiveConnection': self.create_random_name(prefix='test-receive-connection-', length=30),
            'sendFlow': self.create_random_name(prefix='test-send-flow-', length=30),
            'receiveFlow': self.create_random_name(prefix='test-receive-flow-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
            'storageAccountId': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageAccount': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageContainer': 'armstrong-test-containers',
        })

        count = len(self.cmd('az azure-data-transfer pipeline list --resource-group {rg}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pipeline count expected to be more than or equal to 1')

        self.cmd('az azure-data-transfer pipeline show --resource-group {rg} --name {pipeline}', checks=[
            self.check('name', '{pipeline}'),
        ])

        id = self.cmd('az azure-data-transfer connection create --resource-group {rg} --connection-name {receiveConnection} --direction Receive --location {location} --flow-types ["Mission"] --pipeline {pipeline} --justification required --remote-subscription-id {subscriptionId}  --requirement-id 1234 --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com').get_output_in_json().get('id')