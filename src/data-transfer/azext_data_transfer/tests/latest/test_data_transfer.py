# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (
    ScenarioTest, record_only)

class ConnectionAndFlowOperations(ScenarioTest):
    
    @record_only()
    def test_pipeline_view_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'pipeline': 'corptest',
        })

        count = len(self.cmd('az data-transfer pipeline list --resource-group {rg}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pipeline count expected to be more than or equal to 1')

        self.cmd('az data-transfer pipeline show --resource-group {rg} --name {pipeline}', checks=[
            self.check('name', '{pipeline}'),
        ])

    @record_only()
    def test_reject_connection_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'rejectedConnection': self.create_random_name(prefix='test-reject-connection-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
        })

        id = self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {rejectedConnection} --direction Receive --location {location} --flow-types ["Mission"] --pipeline {pipeline} --justification required --remote-subscription-id {subscriptionId}  --requirement-id 1234 --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com').get_output_in_json().get('id')
        self.kwargs.update({'id': id})

        self.cmd('az data-transfer pipeline reject-connection --resource-group {rg} --pipeline-name {pipeline} --id {id}', checks=[
            self.check('properties.status', 'Rejected'),
        ])

        result = self.cmd('az data-transfer pipeline approve-connection --resource-group {rg} --pipeline-name {pipeline} --id {id}', expect_failure=True)

        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {rejectedConnection}')

    @record_only()
    def test_update_connection_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'connectionName': self.create_random_name(prefix='test-update-connection-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
        })

        self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {connectionName} --direction Receive --location {location} --flow-types ["Mission"] --pipeline {pipeline} --justification required --remote-subscription-id {subscriptionId}  --requirement-id 1234 --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com').get_output_in_json().get('id')

        self.cmd('az data-transfer connection update --resource-group {rg} --connection-name {connectionName} --tags testAutomation=true key2=value2', checks=[
            self.check('tags.testAutomation', 'true'),
        ])

        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {connectionName}')

    @record_only()
    def test_list_operations_with_pagination(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'sendConnection': self.create_random_name(prefix='test-send-connection-', length=30),
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'sendFlow': self.create_random_name(prefix='test-send-flow-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
            'storageAccountId': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageContainer': 'armstrong-test-containers',
        })

        self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin 12345')

        count = len(self.cmd('az data-transfer connection list --resource-group {rg} --max-items 3').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'connection count expected to be more than or equal to 1')
        self.assertLessEqual(count, 3, 'connection count expected to be less than or equal to 3 as max items are passed as 3')

        send_flows = []
        for _ in range(3):
            name = self.create_random_name(prefix='test-send-flow-', length=30)
            self.kwargs.update({'name': name})
            send_flows.append(name)
            self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {sendConnection} --name {name} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"')
        
        count = len(self.cmd('az data-transfer connection flow list --resource-group {rg} --connection-name {sendConnection}').get_output_in_json())
        self.assertEqual(count, 3, 'flows count expected to be 3')
        count = len(self.cmd('az data-transfer connection flow list --resource-group {rg} --max-items 2 --connection-name {sendConnection}').get_output_in_json())
        self.assertEqual(count, 2, 'flows count expected to be 2 as max items are passed as 2')

        self.kwargs['sendFlows'] = send_flows

        for flowName in self.kwargs['sendFlows']:
                self.kwargs.update({'flowName': flowName})
                self.cmd('az data-transfer connection flow delete --yes --resource-group {rg} --connection-name {sendConnection} --name {flowName}')
        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')
    
    @record_only()
    def test_enable_disable_flow_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'sendConnection': self.create_random_name(prefix='test-send-connection-', length=30),
            'flowName': self.create_random_name(prefix='test-send-flow-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
            'storageAccountId': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageAccount': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageContainer': 'armstrong-test-containers',
        })

        sendId = self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin 123456').get_output_in_json().get('id')
        self.kwargs.update({'sendId': sendId})

        self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {sendConnection} --name {flowName} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"')

        self.cmd('az data-transfer connection flow disable --resource-group {rg} --connection-name {sendConnection} --name {flowName}', checks=[
            self.check('properties.status', 'Disabled'),
        ])

        self.cmd('az data-transfer connection flow show --resource-group {rg} --connection-name {sendConnection} --name {flowName}', checks=[
            self.check('properties.status', 'Disabled'),
        ])

        self.cmd('az data-transfer connection flow enable --resource-group {rg} --connection-name {sendConnection} --name {flowName}',  checks=[
            self.check('properties.status', 'Enabled'),
        ])
        
        self.cmd('az data-transfer connection flow update --resource-group {rg} --name {flowName} --connection-name {sendConnection} --tags testAutomation=true flowUpdate=value', checks=[
            self.check('tags.testAutomation', 'true'),
        ])
 
        self.cmd('az data-transfer connection flow delete --yes --resource-group {rg} --connection-name {sendConnection} --name {flowName}')
        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')

    @record_only()
    def test_create_delete_connection_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'sendConnection': self.create_random_name(prefix='test-send-connection-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
        })

        self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin 123456')

        self.cmd('az data-transfer connection show --resource-group {rg} --name {sendConnection}', checks=[
            self.check('name', '{sendConnection}'),
        ])
 
        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')

        self.cmd('az data-transfer connection show --resource-group {rg} --connection-name {sendConnection}', expect_failure=True)
    
    @record_only()
    def test_create_delete_flow_operations(self):
        self.kwargs.update({
            'rg': 'rpaas-rg',
            'subscriptionId': '389ff96a-b137-405b-a3c8-4d22514708b5',
            'sendConnection': self.create_random_name(prefix='test-send-connection-', length=30),
            'flowName': self.create_random_name(prefix='test-send-flow-', length=30),
            'location': 'eastus',
            'pipeline': 'corptest',
            'storageAccountId': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageAccount': '/subscriptions/389ff96a-b137-405b-a3c8-4d22514708b5/resourceGroups/rpaas-rg-faikh/providers/Microsoft.Storage/storageAccounts/armstrongtest',
            'storageContainer': 'armstrong-test-containers',
        })

        sendId = self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin 123456').get_output_in_json().get('id')
        self.kwargs.update({'sendId': sendId})

        self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {sendConnection} --name {flowName} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"')

        self.cmd('az data-transfer connection flow show --resource-group {rg} --connection-name {sendConnection} --name {flowName}', checks=[
            self.check('name', '{flowName}'),
        ])
 
        self.cmd('az data-transfer connection flow delete --yes --resource-group {rg} --connection-name {sendConnection} --name {flowName}')
        
        self.cmd('az data-transfer connection flow show --resource-group {rg} --connection-name {sendConnection} --name {flowName}', expect_failure=True)

        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')

    @record_only()
    def test_connection_flow_link_operations(self):
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

        id = self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {receiveConnection} --direction Receive --location {location} --flow-types ["Mission"] --pipeline {pipeline} --justification required --remote-subscription-id {subscriptionId}  --requirement-id 1234 --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com').get_output_in_json().get('id')
        self.kwargs.update({'id': id})

        self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"', expect_failure=True)
        
        self.cmd('az data-transfer pipeline approve-connection --resource-group {rg} --pipeline-name {pipeline} --id {id}')
        
        pin = self.cmd('az data-transfer connection show --resource-group {rg} --connection-name {receiveConnection}').get_output_in_json().get('properties').get('pin')
        self.assertIsNotNone(pin, 'pin expected to be not None')
        self.kwargs.update({'pin': pin})

        sendId = self.cmd('az data-transfer connection create --resource-group {rg} --connection-name {sendConnection} --direction Send --location {location} --flow-types ["Mission"] --pipeline {pipeline} --primary-contact lasuredd@microsoft.com --secondary-contacts lasuredd@microsoft.com --pin {pin}').get_output_in_json().get('id')
        self.kwargs.update({'sendId': sendId})

        count = len(self.cmd('az data-transfer connection list-pending-connection --resource-group {rg} --name {receiveConnection}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pending connections count expected to be more than or equal to 1')

        self.cmd('az data-transfer connection link --resource-group {rg} --name {receiveConnection} --id {sendId}').get_output_in_json().get('id')
        
        flowId = self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"').get_output_in_json().get('id')
        self.kwargs.update({'flowId': flowId})

        sendFlowId = self.cmd('az data-transfer connection flow create --resource-group {rg} --connection-name {sendConnection} --name {sendFlow} --flow-type "Mission" --location {location} --status "Enabled" --storage-account {storageAccountId} --storage-container-name {storageContainer} --data-type "Blob"').get_output_in_json().get('id')
        self.kwargs.update({'sendFlowId': sendFlowId})
        self.assertIsNotNone(sendFlowId, 'flow id expected to be not None')

        count = len(self.cmd('az data-transfer connection list-pending-flow --resource-group {rg} --connection-name {receiveConnection}').get_output_in_json())
        self.assertGreaterEqual(count, 1, 'pending flows count expected to be more than or equal to 1')

        self.cmd('az data-transfer connection flow link --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow} --id {sendFlowId}')

        self.cmd('az data-transfer connection flow delete --yes --resource-group {rg} --connection-name {receiveConnection} --name {receiveFlow}')

        self.cmd('az data-transfer connection flow delete --yes --resource-group {rg} --connection-name {sendConnection} --name {sendFlow}')

        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {receiveConnection}')

        self.cmd('az data-transfer connection delete --yes --resource-group {rg} --connection-name {sendConnection}')