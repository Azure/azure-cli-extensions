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
    def test_datashare_azcli(self, resource_group, storage_account):

        self.kwargs.update({
            'SubscriptionId': self.get_subscription_id(),
            'ConsumerSubscription': '00000000-0000-0000-0000-000000000000',  # change this value in live test
            'ConsumerResourceGroup': 'ads_azure_cli_rg',  # this is a pre-existing reosurce group in consumer subscription
            'ConsumerStorageAccount': 'azurecliadsconsumersa',  # this is a pre-existing storage account in consumer subscription
            'ProviderEmail': 'hsrivastava@microsoft.com',  # change this value in live test
            'ConsumerEmail': 'hsrivastava@microsoft.com',  # change this value in live test
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
                     '--role "Storage Blob Data Contributor" '
                     '--assignee-object-id {} '
                     '--assignee-principal-type ServicePrincipal '
                     '--scope {}'.format(accountPrincipalId, storage_account_json['id']))
            time.sleep(10)

        self.cmd('az storage container create '
                 '--account-name {ProviderStorageAccount} '
                 '--name {ProviderContainer}')

        # EXAMPLE: /DataSets/put/DataSets_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{ProviderAccount}" '
                 '--data-set "{{\\"kind\\":\\"Container\\",\\"properties\\":{{\\"containerName\\":\\"{ProviderContainer}\\",\\"filePath\\":\\"2019.png\\",\\"resourceGroup\\":\\"{ProviderResourceGroup}\\",\\"storageAccountName\\":\\"{ProviderStorageAccount}\\",\\"subscriptionId\\":\\"{SubscriptionId}\\"}}}}" '
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

        # EXAMPLE: /Shares/post/Shares_ListSynchronizations
        self.cmd('az datashare list-synchronization '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[])

        # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_ListSynchronizationDetails
        # self.cmd('az datashare list-synchronization-detail '
        #          '--account-name "{ProviderAccount}" '
        #          '--resource-group "{ProviderResourceGroup}" '
        #          '--share-name "{ProviderShare}" '
        #          '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
        #          checks=[])

        # EXAMPLE: /Invitations/put/Invitations_Create
        self.cmd('az datashare invitation create '
                 '--account-name "{ProviderAccount}" '
                 '--target-email "{ConsumerEmail}" '
                 '--name "{ProviderInvitation}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{ProviderInvitation}'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('targetEmail', '{ConsumerEmail}')])

        # EXAMPLE: /Invitations/get/Invitations_ListByShare
        self.cmd('az datashare invitation list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].invitationStatus', 'Pending'),
                         self.check('[0].name', '{ProviderInvitation}'),
                         self.check('[0].resourceGroup', '{ProviderResourceGroup}'),
                         self.check('[0].targetEmail', '{ConsumerEmail}')])

        # EXAMPLE: /Invitations/get/Invitations_Get
        self.cmd('az datashare invitation show '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderInvitation}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{ProviderInvitation}'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('targetEmail', '{ConsumerEmail}')])

        # EXAMPLE: /ConsumerInvitations/post/ConsumerInvitations_RejectInvitation
        # self.cmd('az datashare consumer-invitation reject-invitation '
        #          '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
        #          '--location "East US 2"',
        #          checks=[])

        # EXAMPLE: /Invitations/delete/Invitations_Delete
        # self.cmd('az datashare invitation delete -y '
        #          '--account-name "{ProviderAccount}" '
        #          '--name "{ProviderInvitation}" '
        #          '--resource-group "{ProviderResourceGroup}" '
        #          '--share-name "{ProviderShare}"',
        #           checks=[])

        # Consumer commands

        datashareConsumerAccount = self.cmd('az datashare account create '
                                            '--location "EAST US" '
                                            '--name "{ConsumerAccount}" '
                                            '--resource-group "{ConsumerResourceGroup}" '
                                            '--subscription "{ConsumerSubscription}"',
                                            checks=[self.check('name', '{ConsumerAccount}'),
                                                    self.check('location', 'eastus'),
                                                    self.check('resourceGroup', '{ConsumerResourceGroup}')]).get_output_in_json()

        # EXAMPLE: /ConsumerInvitations/get/ConsumerInvitations_ListInvitations
        invitations = self.cmd('az datashare consumer-invitation list-invitation ',
                               checks=[self.check('[0].invitationStatus', 'Pending'),
                                       self.check('[0].name', '{ProviderInvitation}'),
                                       self.check('[0].shareName', '{ProviderShare}'),
                                       self.check('[0].providerEmail', '{ProviderEmail}')]).get_output_in_json()

        invitationId = invitations[0]['invitationId']
        sourceShareLocation = invitations[0]['location']
        self.kwargs.update({'InvitationId1': invitationId,
                            'Location1': sourceShareLocation})

        # EXAMPLE: /ConsumerInvitations/get/ConsumerInvitations_Get
        self.cmd('az datashare consumer-invitation show '
                 '--invitation-id "{InvitationId1}" '
                 '--subscription "{ConsumerSubscription}" '
                 '--location "{Location1}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{ProviderInvitation}'),
                         self.check('shareName', '{ProviderShare}'),
                         self.check('providerEmail', '{ProviderEmail}')])

        self.cmd('az datashare account wait '
                 '--name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--created '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])

        # EXAMPLE: /ShareSubscriptions/delete/ShareSubscriptions_Delete
        # self.cmd('az datashare share-subscription delete '
        #          '--account-name "{ConsumerAccount}" '
        #          '--resource-group "{ConsumerResourceGroup}" '
        #          '--name "{ConsumerShareSubscription}" '
        #          '--yes '
        #          '--subscription "{ConsumerSubscription}"',
        #          checks=[])

        # EXAMPLE: /ShareSubscriptions/put/ShareSubscriptions_Create
        self.cmd('az datashare share-subscription create '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--invitation-id "{InvitationId1}" '
                 '--source-share-location "{Location1}" '
                 '--name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('invitationId', '{InvitationId1}'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('resourceGroup', '{ConsumerResourceGroup}'),
                         self.check('shareName', '{ProviderShare}'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('sourceShareLocation', '{Location1}')])

        # EXAMPLE: /ShareSubscriptions/get/ShareSubscriptions_Get
        self.cmd('az datashare share-subscription show '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('invitationId', '{InvitationId1}'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('resourceGroup', '{ConsumerResourceGroup}'),
                         self.check('shareName', '{ProviderShare}'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('sourceShareLocation', '{Location1}')])

        # EXAMPLE: /ShareSubscriptions/get/ShareSubscriptions_ListByAccount
        self.cmd('az datashare share-subscription list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].invitationId', '{InvitationId1}'),
                         self.check('[0].name', '{ConsumerShareSubscription}'),
                         self.check('[0].resourceGroup', '{ConsumerResourceGroup}'),
                         self.check('[0].shareName', '{ProviderShare}'),
                         self.check('[0].shareKind', 'CopyBased'),
                         self.check('[0].sourceShareLocation', '{Location1}')])

        # EXAMPLE: /ConsumerSourceDataSets/get/ConsumerSourceDataSets_ListByShareSubscription
        sourceDatasets = self.cmd('az datashare consumer-source-data-set list '
                                  '--account-name "{ConsumerAccount}" '
                                  '--resource-group "{ConsumerResourceGroup}" '
                                  '--share-subscription-name "{ConsumerShareSubscription}" '
                                  '--subscription "{ConsumerSubscription}"',
                                  checks=[self.check('[0].dataSetName', '{ProviderDataset}'),
                                          self.check('[0].dataSetType', 'Container')]).get_output_in_json()
        sourceDatasetId = sourceDatasets[0]['dataSetId']

        storage_account2_json = self.cmd('az storage account show '
                                         '-n {ConsumerStorageAccount} '
                                         '-g {ConsumerResourceGroup} '
                                         '--subscription "{ConsumerSubscription}"').get_output_in_json()

        accountPrincipalId2 = datashareConsumerAccount['identity']['principalId']
        self.kwargs.update({
            "AccountPrincipalId2": accountPrincipalId2,
            "StorageAccountId2": storage_account2_json['id'],
            "SourceDatasetId": sourceDatasetId})

        if self.is_live or self.in_recording:
            import time
            self.cmd('az role assignment create '
                     '--role "Storage Blob Data Contributor" '
                     '--assignee-object-id "{AccountPrincipalId2}" '
                     '--assignee-principal-type ServicePrincipal '
                     '--scope "{StorageAccountId2}" '
                     '--subscription "{ConsumerSubscription}"')
            time.sleep(10)

        # EXAMPLE: /DataSetMappings/put/DataSetMappings_BlobFolderDatasetMapping_Create
        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--blob-folder-data-set-mapping container-name={ConsumerContainer} data-set-id={SourceDatasetId} prefix={ProviderDataset} resource-group={ConsumerResourceGroup} storage-account-name={ConsumerStorageAccount} subscription-id={ConsumerSubscription} ',
                 checks=[self.check('kind', 'BlobFolder'),
                         self.check('name', '{ConsumerDatasetMapping}'),
                         self.check('prefix', '{ProviderDataset}'),
                         self.check('storageAccountName', '{ConsumerStorageAccount}')])

        # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_Synchronize
        self.cmd('az datashare share-subscription synchronize '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--synchronization-mode "Incremental" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('status', 'Succeeded')])

        # EXAMPLE: /DataSetMappings/get/DataSetMappings_Get
        self.cmd('az datashare data-set-mapping show '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('kind', 'BlobFolder'),
                         self.check('name', '{ConsumerDatasetMapping}'),
                         self.check('prefix', '{ProviderDataset}'),
                         self.check('storageAccountName', '{ConsumerStorageAccount}')])

        # EXAMPLE: /DataSetMappings/get/DataSetMappings_ListByShareSubscription
        self.cmd('az datashare data-set-mapping list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].kind', 'BlobFolder'),
                         self.check('[0].name', '{ConsumerDatasetMapping}'),
                         self.check('[0].prefix', '{ProviderDataset}'),
                         self.check('[0].storageAccountName', '{ConsumerStorageAccount}')])

        # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_ListSynchronizations
        self.cmd('az datashare share-subscription list-synchronization '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].synchronizationMode', 'Incremental')])

        # # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_ListSynchronizationDetails
        # self.cmd('az datashare share-subscription list-synchronization-detail '
        #           '--account-name "{ConsumerAccount}" '
        #           '--resource-group "{ConsumerResourceGroup}" '
        #           '--share-subscription-name "{ConsumerShareSubscription}" '
        #           '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" '
        #           '--subscription "{ConsumerSubscription}"',
        #           checks=[])

        # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_ListSourceShareSynchronizationSettings
        self.cmd('az datashare share-subscription list-source-share-synchronization-setting '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].kind', 'ScheduleBased')])

        # EXAMPLE: /Triggers/put/Triggers_Create
        self.cmd('az datashare trigger create '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--scheduled-trigger recurrence-interval="Day" synchronization-mode="Incremental" synchronization-time="2022-02-02T04:47:52" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('recurrenceInterval', 'Day'),
                         self.check('synchronizationMode', 'Incremental')])

        # EXAMPLE: /Triggers/get/Triggers_Get
        self.cmd('az datashare trigger show '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('recurrenceInterval', 'Day'),
                         self.check('synchronizationMode', 'Incremental')])
                        
        # EXAMPLE: /Triggers/get/Triggers_ListByShareSubscription
        self.cmd('az datashare trigger list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].synchronizationMode', 'Incremental')])

        # EXAMPLE: /ProviderShareSubscriptions/get/ProviderShareSubscriptions_ListByShare
        providerShareSubscriptions = self.cmd('az datashare provider-share-subscription list '
                                              '--account-name "{ProviderAccount}" '
                                              '--resource-group "{ProviderResourceGroup}" '
                                              '--share-name "{ProviderShare}"',
                                              checks=[self.check('[0].consumerEmail', '{ConsumerEmail}'),
                                                      self.check('[0].providerEmail', '{ProviderEmail}'),
                                                      self.check('[0].shareSubscriptionStatus', 'Active'),
                                                      self.check('[0].name', '{ConsumerShareSubscription}')]).get_output_in_json()
        shareSubscriptionObjectId = providerShareSubscriptions[0]['shareSubscriptionObjectId']
        self.kwargs.update({'ProviderShareSubscriptionObjectId': shareSubscriptionObjectId})

        # EXAMPLE: /ProviderShareSubscriptions/get/ProviderShareSubscriptions_GetByShare
        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{ProviderAccount}" '
                 '--provider-share-subscription-id "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Active'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        # EXAMPLE: /ProviderShareSubscriptions/post/ProviderShareSubscriptions_Adjust
        # self.cmd('az datashare provider-share-subscription adjust '
        #         '--account-name "{ProviderAccount}" '
        #         '--expiration-date "2022-02-02T04:47:52" '
        #         '--provider-share-subscription-id "{ProviderShareSubscriptionObjectId}" '
        #         '--resource-group "{ProviderResourceGroup}" '
        #         '--share-name "{ProviderShare}"',
        #         checks=[])

        # EXAMPLE: /ProviderShareSubscriptions/post/ProviderShareSubscriptions_Revoke
        # self.cmd('az datashare provider-share-subscription revoke '
        #           '--account-name "{ProviderAccount}" '
        #           '--provider-share-subscription-id "{ProviderShareSubscriptionObjectId}" '
        #           '--resource-group "{ProviderResourceGroup}" '
        #           '--share-name "{ProviderShare}"',
        #           checks=[self.check('status', 'Succeeded')])

        # if self.is_live or self.in_recording:
        #     import time
        #     time.sleep(5)

        # EXAMPLE: /ProviderShareSubscriptions/post/ProviderShareSubscriptions_Reinstate
        # self.cmd('az datashare provider-share-subscription reinstate '
        #          '--account-name "{ProviderAccount}" '
        #          '--provider-share-subscription-id "{ProviderShareSubscriptionObjectId}" '
        #          '--resource-group "{ProviderResourceGroup}" '
        #          '--share-name "{ProviderShare}"',
        #          checks=[self.check('consumerEmail', '{ConsumerEmail}'),          
        #                  self.check('providerEmail', '{ProviderEmail}'),
        #                  self.check('shareSubscriptionStatus', 'Active'),
        #                  self.check('name', '{ConsumerShareSubscription}'),
        #                  self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        # EXAMPLE: /EmailRegistrations/post/EmailRegistrations_RegisterEmail
        # self.cmd('az datashare email-registration register-email '
        #         '--location "East US 2"',
        #         checks=[])

        # EXAMPLE: /EmailRegistrations/post/EmailRegistrations_ActivateEmail
        # self.cmd('az datashare email-registration activate-email '
        #      '--activation-code "djsfhakj2lekowd3wepfklpwe9lpflcd" '
        #      '--location "East US 2"',
        #      checks=[])

        # Clean up

        # EXAMPLE: /ShareSubscriptions/post/ShareSubscriptions_CancelSynchronization
        # self.cmd('az datashare share-subscription cancel-synchronization '
        #           '--account-name "{ConsumerAccount}" '
        #           '--resource-group "{ConsumerResourceGroup}" '
        #           '--share-subscription-name "{ConsumerShareSubscription}" '
        #           '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" '
        #           '--subscription "{ConsumerSubscription}"',
        #           checks=[])

        # EXAMPLE: /SynchronizationSettings/delete/SynchronizationSettings_Delete
        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}" '
                 '--yes',
                 checks=[])

        # EXAMPLE: /DataSets/delete/DataSets_Delete
        self.cmd('az datashare data-set delete '
                  '--account-name "{ProviderAccount}" '
                  '--name "{ProviderDataset}" '
                  '--resource-group "{ProviderResourceGroup}" '
                  '--share-name "{ProviderShare}" '
                  '--yes',
                  checks=[])

        # EXAMPLE: /Shares/delete/Shares_Delete
        self.cmd('az datashare delete '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--name "{ProviderShare}" '
                 '--yes',
                 checks=[])

        # EXAMPLE: /Triggers/delete/Triggers_Delete
        self.cmd('az datashare trigger delete '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])

        # EXAMPLE: /ShareSubscriptions/delete/ShareSubscriptions_Delete
        self.cmd('az datashare share-subscription delete '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--name "{ConsumerShareSubscription}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])

        # EXAMPLE: /Accounts/delete/Accounts_Delete
        self.cmd('az datashare account delete '
                  '--name "{ProviderAccount}" '
                  '--resource-group "{ProviderResourceGroup}" '
                  '--no-wait '
                  '--yes',
                  checks=[])

        # EXAMPLE: /DataSetMappings/delete/DataSetMappings_Delete
        self.cmd('az datashare data-set-mapping delete '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])

        # EXAMPLE: /Accounts/delete/Accounts_Delete
        self.cmd('az datashare account delete '
                  '--name "{ConsumerAccount}" '
                  '--resource-group "{ConsumerResourceGroup}" '
                  '--no-wait '
                  '--yes '
                  '--subscription "{ConsumerSubscription}"',
                  checks=[])