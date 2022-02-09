# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class DataShareManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_provider_rg'[:12], location='eastus', key='ProviderResourceGroup')
    @StorageAccountPreparer(name_prefix='clitestdatashareprovidersa'[:12], location='eastus', key='ProviderStorageAccount')
    @AllowLargeResponse()
    def test_datashare(self, resource_group, storage_account):

        self.kwargs.update({
            'SubscriptionId': self.get_subscription_id(),
            'ConsumerSubscription': '00000000-0000-0000-0000-000000000000',  # change this value in live test
            'ConsumerResourceGroup': 'datashare_consumer_rg',  # this is a pre-existing reosurce group in consumer subscription
            'ConsumerStorageAccount': 'datashareconsumersa',  # this is a pre-existing storage account in consumer subscription
            'ProviderEmail': 'provider@microsoft.com',  # change this value in live test
            'ConsumerEmail': 'consumer@microsoft.com',  # change this value in live test
            'ProviderAccount': 'cli_test_account',
            'ConsumerAccount': 'cli_test_consumer_account',
            'ProviderDataset': 'cli_test_data_set',
            'ConsumerDatasetMapping': 'cli_test_data_set_mapping',
            'ProviderInvitation': 'cli_test_invitation',
            'ProviderShare': 'cli_test_share',
            'ConsumerShareSubscription': 'cli_test_share_subscription',
            'ProviderSynchronizationSetting': 'cli_test_synchronization_setting',
            'ConsumerTrigger': 'cli_test_trigger',
            'ProviderContainer': 'clitestcontainer',
            'ConsumerContainer': 'clitestconsumercontainer',
        })

        # Provider commands

        # EXAMPLE: /Accounts/put/Accounts_Create
        datashareAccount = self.cmd('az datashare account create '
                                    '--location "East US" '
                                    '--tags tag1=Red tag2=White '
                                    '--name "{ProviderAccount}" '
                                    '--resource-group "{ProviderResourceGroup}"',
                                    checks=[self.check('name', '{ProviderAccount}'),
                                            self.check('location', 'eastus'),
                                            self.check('resourceGroup', '{ProviderResourceGroup}'),
                                            self.check('tags.tag1', 'Red'),
                                            self.check('tags.tag2', 'White')
                                            ]).get_output_in_json()

        self.cmd('az datashare account wait '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--created',
                 checks=[])

        accountId = datashareAccount['id']

        # EXAMPLE: /Accounts/get/Accounts_Get
        self.cmd('az datashare account show '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'eastus'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])
        self.cmd('az datashare account show '
                 '--ids {}'.format(accountId),
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'eastus'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

        # EXAMPLE: /Accounts/get/Accounts_ListByResourceGroup
        self.cmd('az datashare account list '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), '{ProviderAccount}'),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'eastus'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), '{ProviderResourceGroup}'),
                         self.check("[?id=='{}'].tags | [0].tag1".format(accountId), 'Red'),
                         self.check("[?id=='{}'].tags | [0].tag2".format(accountId), 'White')])

        # EXAMPLE: /Accounts/get/Accounts_ListBySubscription
        self.cmd('az datashare account list '
                 '-g ""',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), '{ProviderAccount}'),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'eastus'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), '{ProviderResourceGroup}'),
                         self.check("[?id=='{}'].tags | [0].tag1".format(accountId), 'Red'),
                         self.check("[?id=='{}'].tags | [0].tag2".format(accountId), 'White')])

        # EXAMPLE: /Accounts/patch/Accounts_Update
        self.cmd('az datashare account update '
                 '--name "{ProviderAccount}" '
                 '--tags tag1=Green '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'eastus'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Green')])

        # EXAMPLE: /Shares/put/Shares_Create
        datashare = self.cmd('az datashare create '
                             '--account-name "{ProviderAccount}" '
                             '--resource-group "{ProviderResourceGroup}" '
                             '--description "share description" '
                             '--share-kind "CopyBased" '
                             '--terms "Confidential" '
                             '--name "{ProviderShare}"',
                             checks=[self.check('name', '{ProviderShare}'),
                                     self.check('description', 'share description'),
                                     self.check('shareKind', 'CopyBased'),
                                     self.check('terms', 'Confidential')]).get_output_in_json()

        datashareId = datashare['id']

        # EXAMPLE: /Shares/get/Shares_Get
        self.cmd('az datashare show '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--name "{ProviderShare}"',
                 checks=[self.check('name', '{ProviderShare}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

        self.cmd('az datashare show '
                 '--ids {}'.format(datashareId),
                 checks=[self.check('name', '{ProviderShare}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

        # EXAMPLE: /Shares/get/Shares_ListByAccount
        self.cmd('az datashare list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(datashareId), '{ProviderShare}'),
                         self.check("[?id=='{}'].description | [0]".format(datashareId), 'share description'),
                         self.check("[?id=='{}'].shareKind | [0]".format(datashareId), 'CopyBased'),
                         self.check("[?id=='{}'].terms | [0]".format(datashareId), 'Confidential')])

        storage_account_json = self.cmd('az storage account show '
                                        '-n {ProviderStorageAccount} '
                                        '-g {ProviderResourceGroup}').get_output_in_json()

        accountPrincipalId = datashareAccount['identity']['principalId']

        if self.is_live or self.in_recording:
            import time
            self.cmd('az role assignment create '
                     '--role "Storage Blob Data Contributor" '  # Storage Blob Data Reader
                     '--assignee-object-id {} '
                     '--assignee-principal-type ServicePrincipal '
                     '--scope {}'.format(accountPrincipalId, storage_account_json['id']))
            time.sleep(10)

        self.cmd('az storage container create '
                 '--account-name {ProviderStorageAccount} '
                 '--name {ProviderContainer}')

        datasetContent = {"container-name": "{}".format(self.kwargs.get('ProviderContainer', '')), "storage-account-name": "{}".format(storage_account), "kind": "Container"}
        self.kwargs.update({
            'ProviderDatasetContent': datasetContent
        })
        self.cmd('az datashare data-set create '
                 '--account-name "{ProviderAccount}" '
                 '--blob-container-data-set container-name={ProviderContainer} storage-account-name={ProviderStorageAccount} subscription-id={SubscriptionId} resource-group={ProviderResourceGroup} '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('containerName', '{ProviderContainer}'),
                         self.check('storageAccountName', '{ProviderStorageAccount}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{ProviderDataset}')])
        
        # EXAMPLE: /DataSets/get/DataSets_Get
        self.cmd('az datashare data-set show '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('containerName', '{ProviderContainer}'),
                         self.check('storageAccountName', '{ProviderStorageAccount}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{ProviderDataset}')])

        # EXAMPLE: /DataSets/get/DataSets_ListByShare
        self.cmd('az datashare data-set list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].containerName', '{ProviderContainer}'),
                         self.check('[0].storageAccountName', '{ProviderStorageAccount}'),
                         self.check('[0].kind', 'Container'),
                         self.check('[0].name', '{ProviderDataset}')])

        # EXAMPLE: /SynchronizationSettings/put/SynchronizationSettings_Create
        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}" '
                 '--scheduled-synchronization-setting recurrence-interval="Day" synchronization-time="2022-02-02T04:47:52" ',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{ProviderSynchronizationSetting}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('synchronizationTime', '2022-02-02T04:47:52+00:00')])

        # EXAMPLE: /SynchronizationSettings/get/SynchronizationSettings_Get
        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}"',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{ProviderSynchronizationSetting}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('synchronizationTime', '2022-02-02T04:47:52+00:00')])

        # EXAMPLE: /SynchronizationSettings/get/SynchronizationSettings_ListByShare
        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].kind', 'ScheduleBased'),
                         self.check('[0].name', '{ProviderSynchronizationSetting}'),
                         self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].resourceGroup', '{ProviderResourceGroup}'),
                         self.check('[0].synchronizationTime', '2022-02-02T04:47:52+00:00')])

        # Provider Clean up

        # EXAMPLE: /DataSets/delete/DataSets_Delete
        self.cmd('az datashare data-set delete '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--yes',
                 checks=[])

        self.cmd('az datashare account delete '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--no-wait '
                 '--yes',
                 checks=[])