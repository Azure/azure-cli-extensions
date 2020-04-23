# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataShareManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_provider_rg'[:12], location='westus2', key='ProviderResourceGroup')
    @StorageAccountPreparer(name_prefix='clitestdatashareprovidersa'[:12], location='westus2', key='ProviderStorageAccount')
    @AllowLargeResponse()
    def test_datashare(self, resource_group, storage_account):

        self.kwargs.update({
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
        datashareAccount = self.cmd('az datashare account create '
                                    '--location "West US 2" '
                                    '--tags tag1=Red tag2=White '
                                    '--name "{ProviderAccount}" '
                                    '--resource-group "{ProviderResourceGroup}"',
                                    checks=[self.check('name', '{ProviderAccount}'),
                                            self.check('location', 'westus2'),
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
        self.cmd('az datashare account show '
                 '-n "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

        self.cmd('az datashare account show '
                 '--ids {}'.format(accountId),
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

        self.cmd('az datashare account list '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), '{ProviderAccount}'),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'westus2'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), '{ProviderResourceGroup}'),
                         self.check("[?id=='{}'].tags | [0].tag1".format(accountId), 'Red'),
                         self.check("[?id=='{}'].tags | [0].tag2".format(accountId), 'White')])

        self.cmd('az datashare account update '
                 '--name "{ProviderAccount}" '
                 '--tags tag1=Green '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Green')])

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

        self.cmd('az datashare show '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--name "{ProviderShare}"',
                 checks=[self.check('name', '{ProviderShare}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

        datashareId = datashare['id']
        self.cmd('az datashare show '
                 '--ids {}'.format(datashareId),
                 checks=[self.check('name', '{ProviderShare}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

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
                     '--role "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1" '  # Storage Blob Data Reader
                     '--assignee-object-id {} '
                     '--assignee-principal-type ServicePrincipal '
                     '--scope {}'.format(accountPrincipalId, storage_account_json['id']))
            time.sleep(5)

        self.cmd('az storage container create '
                 '--account-name {ProviderStorageAccount} '
                 '--name {ProviderContainer}')

        datasetContent = {"container_name": "{}".format(self.kwargs.get('ProviderContainer', '')), "storage_account_name": "{}".format(storage_account), "kind": "Container"}
        self.kwargs.update({
            'ProviderDatasetContent': datasetContent
        })
        self.cmd('az datashare dataset create '
                 '--account-name "{ProviderAccount}" '
                 '--dataset "{ProviderDatasetContent}" '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('containerName', '{ProviderContainer}'),
                         self.check('storageAccountName', '{ProviderStorageAccount}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{ProviderDataset}')])

        self.cmd('az datashare dataset show '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('containerName', '{ProviderContainer}'),
                         self.check('storageAccountName', '{ProviderStorageAccount}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{ProviderDataset}')])

        self.cmd('az datashare dataset list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].containerName', '{ProviderContainer}'),
                         self.check('[0].storageAccountName', '{ProviderStorageAccount}'),
                         self.check('[0].kind', 'Container'),
                         self.check('[0].name', '{ProviderDataset}')])

        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}" '
                 '--recurrence-interval "Day" '
                 '--synchronization-time "2020-04-05 10:50:00 +00:00"',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{ProviderSynchronizationSetting}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}"',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{ProviderSynchronizationSetting}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].kind', 'ScheduleBased'),
                         self.check('[0].name', '{ProviderSynchronizationSetting}'),
                         self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].resourceGroup', '{ProviderResourceGroup}'),
                         self.check('[0].synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare synchronization list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[])

        # self.cmd('az datashare synchronization list-detail '
        #          '--account-name "{ProviderAccount}" '
        #          '--resource-group "{ProviderResourceGroup}" '
        #          '--share-name "{ProviderShare}" '
        #          '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
        #          checks=[])

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

        self.cmd('az datashare invitation list '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('[0].invitationStatus', 'Pending'),
                         self.check('[0].name', '{ProviderInvitation}'),
                         self.check('[0].resourceGroup', '{ProviderResourceGroup}'),
                         self.check('[0].targetEmail', '{ConsumerEmail}')])

        self.cmd('az datashare invitation show '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderInvitation}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{ProviderInvitation}'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('targetEmail', '{ConsumerEmail}')])

        # Consumer commands
        datashareConsumerAccount = self.cmd('az datashare account create '
                                            '--location "West US 2" '
                                            '--name "{ConsumerAccount}" '
                                            '--resource-group "{ConsumerResourceGroup}" '
                                            '--subscription "{ConsumerSubscription}"',
                                            checks=[self.check('name', '{ConsumerAccount}'),
                                                    self.check('location', 'westus2'),
                                                    self.check('resourceGroup', '{ConsumerResourceGroup}')]).get_output_in_json()

        invitations = self.cmd('az datashare consumer invitation list '
                               '--subscription "{ConsumerSubscription}"',
                               checks=[self.check('[0].invitationStatus', 'Pending'),
                                       self.check('[0].name', '{ProviderInvitation}'),
                                       self.check('[0].shareName', '{ProviderShare}'),
                                       self.check('[0].providerEmail', '{ProviderEmail}')]).get_output_in_json()

        invitationId = invitations[0]['invitationId']
        sourceShareLocation = invitations[0]['location']
        self.kwargs.update({'InvitationId1': invitationId,
                            'Location1': sourceShareLocation})

        self.cmd('az datashare consumer invitation show '
                 '--invitation-id "{InvitationId1}" '
                 '--subscription "{ConsumerSubscription}" '
                 '--location "{Location1}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{ProviderInvitation}'),
                         self.check('shareName', '{ProviderShare}'),
                         self.check('providerEmail', '{ProviderEmail}')])

#         self.cmd('az datashare consumer invitation reject '
#                  '--invitation-id 00000000-0000-0000-0000-000000000000 '
#                  checks=[])

        self.cmd('az datashare account wait '
                 '--name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--created '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])

        self.cmd('az datashare consumer share-subscription create '
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

        self.cmd('az datashare consumer share-subscription show '
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

        self.cmd('az datashare consumer share-subscription list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].invitationId', '{InvitationId1}'),
                         self.check('[0].name', '{ConsumerShareSubscription}'),
                         self.check('[0].resourceGroup', '{ConsumerResourceGroup}'),
                         self.check('[0].shareName', '{ProviderShare}'),
                         self.check('[0].shareKind', 'CopyBased'),
                         self.check('[0].sourceShareLocation', '{Location1}')])

        sourceDatasets = self.cmd('az datashare consumer share-subscription list-source-dataset '
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
            "StorageAccountId2": storage_account2_json['id']})

        if self.is_live or self.in_recording:
            import time
            self.cmd('az role assignment create '
                     '--role "ba92f5b4-2d11-453d-a403-e96b0029c9fe" '  # Storage Blob Data Contributor
                     '--assignee-object-id "{AccountPrincipalId2}" '
                     '--assignee-principal-type ServicePrincipal '
                     '--scope "{StorageAccountId2}" '
                     '--subscription "{ConsumerSubscription}"')
            time.sleep(5)

        datasetMappingContent = {"data_set_id": "{}".format(sourceDatasetId),
                                 "container_name": "{}".format(self.kwargs.get('ConsumerContainer', '')),
                                 "storage_account_name": "{}".format(self.kwargs.get('ConsumerStorageAccount', '')),
                                 "kind": "BlobFolder",
                                 "prefix": "{}".format(self.kwargs.get('ProviderDataset', ''))}
        self.kwargs.update({
            'ConsumerDatasetMappingContent': datasetMappingContent
        })
        self.cmd('az datashare consumer dataset-mapping create '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--mapping "{ConsumerDatasetMappingContent}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('kind', 'BlobFolder'),
                         self.check('name', '{ConsumerDatasetMapping}'),
                         self.check('prefix', '{ProviderDataset}'),
                         self.check('storageAccountName', '{ConsumerStorageAccount}')])

        self.cmd('az datashare consumer share-subscription synchronization start '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--synchronization-mode "Incremental" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('status', 'Queued'),
                         self.check('synchronizationMode', 'Incremental')])

        self.cmd('az datashare consumer dataset-mapping show '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('kind', 'BlobFolder'),
                         self.check('name', '{ConsumerDatasetMapping}'),
                         self.check('prefix', '{ProviderDataset}'),
                         self.check('storageAccountName', '{ConsumerStorageAccount}')])

        self.cmd('az datashare consumer dataset-mapping list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].kind', 'BlobFolder'),
                         self.check('[0].name', '{ConsumerDatasetMapping}'),
                         self.check('[0].prefix', '{ProviderDataset}'),
                         self.check('[0].storageAccountName', '{ConsumerStorageAccount}')])

        self.cmd('az datashare consumer share-subscription synchronization list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].synchronizationMode', 'Incremental')])

#         self.cmd('az datashare consumer share-subscription synchronization list-detail '
#                  '--account-name "{ConsumerAccount}" '
#                  '--resource-group "{ConsumerResourceGroup}" '
#                  '--share-subscription-name "{ConsumerShareSubscription}" '
#                  '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" '
#                  '--subscription "{ConsumerSubscription}"',
#                  checks=[])

#         self.cmd('az datashare consumer share-subscription synchronization cancel '
#                  '--account-name "{ConsumerAccount}" '
#                  '--resource-group "{ConsumerResourceGroup}" '
#                  '--share-subscription-name "{ConsumerShareSubscription}" '
#                  '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb" '
#                  '--subscription "{ConsumerSubscription}"',
#                  checks=[])

        self.cmd('az datashare consumer share-subscription list-source-share-synchronization-setting '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].kind', 'ScheduleBased')])

        self.cmd('az datashare consumer trigger create '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--recurrence-interval "Day" '
                 '--synchronization-time "2020-04-05 10:50:00 +00:00" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('properties.recurrenceInterval', 'Day'),  # TODO properties is not removed in the response structure
                         self.check('properties.synchronizationMode', 'Incremental')])

        self.cmd('az datashare consumer trigger show '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('recurrenceInterval', 'Day'),
                         self.check('synchronizationMode', 'Incremental')])

        self.cmd('az datashare consumer trigger list '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].synchronizationMode', 'Incremental')])

        # Provider commands
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

        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{ProviderAccount}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Active'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        self.cmd('az datashare provider-share-subscription revoke '
                 '--account-name "{ProviderAccount}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Revoking'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        if self.is_live or self.in_recording:
            import time
            time.sleep(5)

        self.cmd('az datashare provider-share-subscription reinstate '
                 '--account-name "{ProviderAccount}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Active'),
                         self.check('name', '{ConsumerShareSubscription}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        # Provider Clean up
        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--name "{ProviderSynchronizationSetting}" '
                 '--yes',
                 checks=[])

        # self.cmd('az datashare invitation delete '
        #          '--account-name "{ProviderAccount}" '
        #          '--name "{ProviderInvitation}" '
        #          '--resource-group "{ProviderResourceGroup}" '
        #          '--share-name "{ProviderShare}"',
        #          checks=[])

        self.cmd('az datashare dataset delete '
                 '--account-name "{ProviderAccount}" '
                 '--name "{ProviderDataset}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--share-name "{ProviderShare}" '
                 '--yes',
                 checks=[])

        self.cmd('az datashare delete '
                 '--account-name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--name "{ProviderShare}" '
                 '--yes',
                 checks=[])

        self.cmd('az datashare account delete '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--no-wait '
                 '--yes',
                 checks=[])

        self.cmd('az datashare consumer trigger delete '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--name "{ConsumerTrigger}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])
        self.cmd('az datashare consumer dataset-mapping delete '
                 '--account-name "{ConsumerAccount}" '
                 '--name "{ConsumerDatasetMapping}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--share-subscription-name "{ConsumerShareSubscription}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])
        self.cmd('az datashare consumer share-subscription delete '
                 '--account-name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--name "{ConsumerShareSubscription}" '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])
        self.cmd('az datashare account delete '
                 '--name "{ConsumerAccount}" '
                 '--resource-group "{ConsumerResourceGroup}" '
                 '--no-wait '
                 '--yes '
                 '--subscription "{ConsumerSubscription}"',
                 checks=[])
