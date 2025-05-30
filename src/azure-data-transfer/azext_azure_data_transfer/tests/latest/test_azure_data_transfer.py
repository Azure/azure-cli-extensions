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
            'storageContainer': 'armstrong-test-containerd',
        })

        count = len(self.cmd('az azure-data-transfer pipeline list --resource-group {rg}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pipeline count expected to be more than or equal to 1')

        self.cmd('az azure-data-transfer pipeline show --resource-group {rg} --name {pipeline}', checks=[
            self.check('name', '{pipeline}'),
        ])

        id = self.cmd('az azure-data-transfer connection create --resource-group {rg} --connection-name {receiveConnection} --direction Receive --location {location} --flow-types ["Mission"] --pipeline {pipeline} --justification required --remote-subscription-id {subscriptionId}  --requirement-id 1234 --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com').get_output_in_json().get('id')
        self.cmd('az azure-data-transfer connection show --resource-group {rg} --name {receiveConnection}', checks=[
            self.check('name', '{receiveConnection}'),
        ])
        self.kwargs.update({'id': id})

        count = len(self.cmd('az azure-data-transfer connection list --resource-group {rg}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'connection count expected to be more than or equal to 1')

        self.cmd('az azure-data-transfer pipeline approve-connection --resource-group {rg} --name {pipeline} --id {id}')
        
        pin = self.cmd('az azure-data-transfer connection show --resource-group {rg} --connection-name {receiveConnection}').get_output_in_json().get('properties').get('pin')
        self.assertIsNotNone(pin, 'pin expected to be not None')
        self.kwargs.update({'pin': pin})

        sendId = self.cmd('az azure-data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin {pin}').get_output_in_json().get('id')
        self.kwargs.update({'sendId': sendId})

        count = len(self.cmd('az azure-data-transfer connection list-pending-connection --resource-group {rg} --name {receiveConnection}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pending connections count expected to be more than or equal to 1')

        self.cmd('az azure-data-transfer connection link --resource-group {rg} --name {receiveConnection} --id {sendId}').get_output_in_json().get('id')

        flowId = self.cmd('az azure-data-transfer connection flow create --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow} --flow-type "Mission" --location {location} --status "Enabled" --storage-account-id {storageAccountId} --storage-account-name {storageAccount} --storage-container-name {storageContainer} --data-type "Blob"').get_output_in_json().get('id')
        self.kwargs.update({'flowId': flowId})

        sendFlowId = self.cmd('az azure-data-transfer connection flow create --resource-group {rg} --connection-name {sendConnection} --name {sendFlow} --flow-type "Mission" --location {location} --status "Enabled" --storage-account-id {storageAccountId} --storage-account-name {storageAccount} --storage-container-name {storageContainer} --data-type "Blob"').get_output_in_json().get('id')
        self.kwargs.update({'sendFlowId': sendFlowId})
        self.assertIsNotNone(sendFlowId, 'flow id expected to be not None')

        count = len(self.cmd('az azure-data-transfer connection flow list --resource-group {rg} --connection-name {receiveConnection}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'flows count expected to be more than or equal to 1')

        count = len(self.cmd('az azure-data-transfer connection list-pending-flow --resource-group {rg} --connection-name {receiveConnection}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pending flows count expected to be more than or equal to 1')

        self.cmd('az azure-data-transfer connection flow link --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow} --id {sendFlowId}')

        self.cmd('az azure-data-transfer connection flow disable --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow}')

        self.cmd('az azure-data-transfer connection flow show --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow}', checks=[
            self.check('properties.status', 'Disabled'),
        ])

        self.cmd('az azure-data-transfer connection flow enable --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow}',  checks=[
            self.check('properties.status', 'Enabled'),
        ])
        
        self.cmd('az azure-data-transfer connection flow update --resource-group {rg} --name {sendFlow} --connection-name {sendConnection} --storage-container "UpdatedStorage"', checks=[
            self.check('properties.storageContainerName', 'UpdatedStorage'),
        ])

        self.cmd('az azure-data-transfer connection flow delete --yes --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow}')

        self.cmd('az azure-data-transfer connection flow delete --yes --resource-group {rg} --connection-name {sendConnection} --name {sendFlow}')

        self.cmd('az azure-data-transfer connection delete --yes --resource-group {rg} --connection-name {receiveConnection}')

        self.cmd('az azure-data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')
