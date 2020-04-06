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

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_SampleResourceGroup'[:9], key='rg')
    @StorageAccountPreparer(name_prefix='clitestdatasharesa', key='sa')
    def test_datashare(self, resource_group, storage_account):

        self.kwargs.update({
            'ProviderSubscription': '0b1f6471-1bf0-4dda-aec3-cb9272f09590',
            'ConsumerSubscription': '9abff005-2afc-4de1-b39c-344b9de2cc9c',
            'ProviderEmail': 'feng.zhou@microsoft.com',
            'ConsumerEmail': 'fengzhou810@163.com',
            'Account1': self.create_random_name(prefix='cli_test_accounts'[:9], length=24),
            'Account2': self.create_random_name(prefix='cli_test_acc_consumer'[:9], length=24),
            'Dataset1': self.create_random_name(prefix='cli_test_data_sets'[:9], length=24),
            'DatasetMapping1': self.create_random_name(prefix='cli_test_data_set_mappings'[:9], length=24),
            'Invitation1': self.create_random_name(prefix='cli_test_invitations'[:9], length=24),
            'Share1': self.create_random_name(prefix='cli_test_shares'[:9], length=24),
            'ShareSubscription1': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_2': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_3': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'SynchronizationSettings_2': self.create_random_name(prefix='cli_test_synchronization_settings'[:9], length=24),
            'Trigger1': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
            'Container1': self.create_random_name(prefix='clitestcontainer'[:9], length=24),
            'rg': resource_group,
            'sa': storage_account,
            'rg2': 'feng-cli-rg',
            'sa2': 'copyextsa',
            'Container2': self.create_random_name(prefix='clitestconsumercontainer'[:9], length=24),
        })
        print(self.kwargs)
        # Provider commands
        datashareAccount = self.cmd('az datashare account create '
                                    '--identity type=SystemAssigned '
                                    '--location "West US 2" '
                                    '--tags tag1=Red tag2=White '
                                    '--name "{Account1}" '
                                    '--resource-group "{rg}"',
                                    checks=[self.check('name', '{Account1}'),
                                            self.check('location', 'westus2'),
                                            self.check('resourceGroup', '{rg}'),
                                            self.check('tags.tag1', 'Red'),
                                            self.check('tags.tag2', 'White')
                                            ]).get_output_in_json()
        self.cmd('az datashare account create '
                 '--identity type=SystemAssigned '
                 '--location "West US 2" '
                 '--tags tag1=Red tag2=White '
                 '--name "{Account2}" '
                 '--resource-group "{rg}"',
                 checks=[self.check('name', '{Account2}'),
                         self.check('location', 'westus2'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ]).get_output_in_json()
        self.cmd('az datashare account wait '
                 '--name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--created',
                 checks=[])

        accountId = datashareAccount['id']
        self.cmd('az datashare account show '
                 '-n "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[self.check('name', '{Account1}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

        self.cmd('az datashare account show '
                 '--ids {}'.format(accountId),
                 checks=[self.check('name', '{Account1}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

        self.cmd('az datashare account list '
                 '--resource-group "{rg}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), '{Account1}'),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'westus2'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), '{rg}'),
                         self.check("[?id=='{}'].tags | [0].tag1".format(accountId), 'Red'),
                         self.check("[?id=='{}'].tags | [0].tag2".format(accountId), 'White')])

        self.cmd('az datashare account update '
                 '--name "{Account1}" '
                 '--tags tag1=Green '
                 '--resource-group "{rg}"',
                 checks=[self.check('name', '{Account1}'),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('tags.tag1', 'Green')])

        datashare = self.cmd('az datashare create '
                             '--account-name "{Account1}" '
                             '--resource-group "{rg}" '
                             '--description "share description" '
                             '--share-kind "CopyBased" '
                             '--terms "Confidential" '
                             '--name "{Share1}"',
                             checks=[self.check('name', '{Share1}'),
                                     self.check('description', 'share description'),
                                     self.check('shareKind', 'CopyBased'),
                                     self.check('terms', 'Confidential')]).get_output_in_json()

        self.cmd('az datashare show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--name "{Share1}"',
                 checks=[self.check('name', '{Share1}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

        datashareId = datashare['id']
        self.cmd('az datashare show '
                 '--ids {}'.format(datashareId),
                 checks=[self.check('name', '{Share1}'),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])

        self.cmd('az datashare list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(datashareId), '{Share1}'),
                         self.check("[?id=='{}'].description | [0]".format(datashareId), 'share description'),
                         self.check("[?id=='{}'].shareKind | [0]".format(datashareId), 'CopyBased'),
                         self.check("[?id=='{}'].terms | [0]".format(datashareId), 'Confidential')])

        storage_account_json = self.cmd('az storage account show '
                                        '-n {sa} '
                                        '-g {rg}').get_output_in_json()
        print(storage_account_json)
        accountPrincipalId = datashareAccount['identity']['principalId']
        self.cmd('az role assignment create '
                 '--role "Storage Blob Data Reader" '  # 2a2b9908-6ea1-4ae2-8e65-a410df84e7d1
                 '--assignee-object-id {} '
                 '--assignee-principal-type ServicePrincipal '
                 '--scope {}'.format(accountPrincipalId, storage_account_json['id']))

        self.cmd('az storage container create '
                 '--account-name {sa} '
                 '--name {Container1}')

        datasetContent = {"container_name": "{}".format(self.kwargs.get('Container1', '')), "storage_account_name": "{}".format(storage_account), "kind": "Container"}
        self.kwargs.update({
            'DatasetContent1': datasetContent
        })
        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--dataset "{DatasetContent1}" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('containerName', '{Container1}'),
                         self.check('storageAccountName', '{sa}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{Dataset1}')])

        self.cmd('az datashare dataset show '
                 '--account-name "{Account1}" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('containerName', '{Container1}'),
                         self.check('storageAccountName', '{sa}'),
                         self.check('kind', 'Container'),
                         self.check('name', '{Dataset1}')])

        self.cmd('az datashare dataset list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('[0].containerName', '{Container1}'),
                         self.check('[0].storageAccountName', '{sa}'),
                         self.check('[0].kind', 'Container'),
                         self.check('[0].name', '{Dataset1}')])

        syncSettingContent = {"recurrenceInterval": "Day", "synchronizationTime": "2020-04-05T10:50:00Z", "kind": "ScheduleBased"}
        self.kwargs.update({
            'SyncSettingContent1': syncSettingContent
        })
        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--name "{SynchronizationSettings_2}" '
                 '--setting "{SyncSettingContent1}"',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{SynchronizationSettings_2}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--name "{SynchronizationSettings_2}"',
                 checks=[self.check('kind', 'ScheduleBased'),
                         self.check('name', '{SynchronizationSettings_2}'),
                         self.check('recurrenceInterval', 'Day'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('[0].kind', 'ScheduleBased'),
                         self.check('[0].name', '{SynchronizationSettings_2}'),
                         self.check('[0].recurrenceInterval', 'Day'),
                         self.check('[0].resourceGroup', '{rg}'),
                         self.check('[0].synchronizationTime', '2020-04-05T10:50:00+00:00')])

        self.cmd('az datashare list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # self.cmd('az datashare list-synchronization-detail '
        #          '--account-name "{Account1}" '
        #          '--resource-group "{rg}" '
        #          '--share-name "{Share1}" '
        #          '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
        #          checks=[])

        self.cmd('az datashare invitation create '
                 '--account-name "{Account1}" '
                 '--target-email "{ConsumerEmail}" '
                 '--name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{Invitation1}'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('targetEmail', '{ConsumerEmail}')])

        self.cmd('az datashare invitation list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('[0].invitationStatus', 'Pending'),
                         self.check('[0].name', '{Invitation1}'),
                         self.check('[0].resourceGroup', '{rg}'),
                         self.check('[0].targetEmail', '{ConsumerEmail}')])

        self.cmd('az datashare invitation show '
                 '--account-name "{Account1}" '
                 '--name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{Invitation1}'),
                         self.check('resourceGroup', '{rg}'),
                         self.check('targetEmail', '{ConsumerEmail}')])

        # Consumer commands
        self.cmd('az account set -s "{ConsumerSubscription}"')
        datashareAccount2 = self.cmd('az datashare account create '
                                     '--identity type=SystemAssigned '
                                     '--location "West US 2" '
                                     '--name "{Account2}" '
                                     '--resource-group "{rg2}"',
                                     checks=[self.check('name', '{Account2}'),
                                             self.check('location', 'westus2'),
                                             self.check('resourceGroup', '{rg2}')]).get_output_in_json()

        invitations = self.cmd('az datashare consumer-invitation list',
                               checks=[self.check('[0].invitationStatus', 'Pending'),
                                       self.check('[0].name', '{Invitation1}'),
                                       self.check('[0].shareName', '{Share1}'),
                                       self.check('[0].providerEmail', '{ProviderEmail}')]).get_output_in_json()

        invitationId = invitations[0]['invitationId']
        sourceShareLocation = invitations[0]['location']
        self.kwargs.update({'InvitationId1': invitationId,
                            'Location1': sourceShareLocation})

        self.cmd('az datashare consumer-invitation show '
                 '--invitation-id "{InvitationId1}"',
                 checks=[self.check('invitationStatus', 'Pending'),
                         self.check('name', '{Invitation1}'),
                         self.check('shareName', '{Share1}'),
                         self.check('providerEmail', '{ProviderEmail}')])

#         self.cmd('az datashare consumer-invitation reject-invitation '
#                  '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
#                  '--location "East US 2"',
#                  checks=[])

        self.cmd('az datashare account wait '
                 '--name "{Account2}" '
                 '--resource-group "{rg2}" '
                 '--created',
                 checks=[])

        self.cmd('az datashare share-subscription create '
                 '--account-name "{Account2}" '
                 '--resource-group "{rg2}" '
                 '--invitation-id "{InvitationId1}" '
                 '--source-share-location "{Location1}" '
                 '--name "{ShareSubscription1}"',
                 checks=[self.check('invitationId', '{InvitationId1}'),
                         self.check('name', '{ShareSubscription1}'),
                         self.check('resourceGroup', '{rg2}'),
                         self.check('shareName', '{Share1}'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('sourceShareLocation', '{Location1}')])

        self.cmd('az datashare share-subscription show '
                 '--account-name "{Account2}" '
                 '--resource-group "{rg2}" '
                 '--name "{ShareSubscription1}"',
                 checks=[self.check('invitationId', '{InvitationId1}'),
                         self.check('name', '{ShareSubscription1}'),
                         self.check('resourceGroup', '{rg2}'),
                         self.check('shareName', '{Share1}'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('sourceShareLocation', '{Location1}')])

        self.cmd('az datashare share-subscription list '
                 '--account-name "{Account2}" '
                 '--resource-group "{rg2}"',
                 checks=[self.check('[0].invitationId', '{InvitationId1}'),
                         self.check('[0].name', '{ShareSubscription1}'),
                         self.check('[0].resourceGroup', '{rg2}'),
                         self.check('[0].shareName', '{Share1}'),
                         self.check('[0].shareKind', 'CopyBased'),
                         self.check('[0].sourceShareLocation', '{Location1}')])

#         self.cmd('az datashare share-subscription list-synchronization '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscriptions_3}"',
#                  checks=[])
# # [
# #   {
# #     "durationMs": 23116,
# #     "endTime": "2020-04-05T06:30:17.285764+00:00",
# #     "message": null,
# #     "startTime": "2020-04-05T06:29:54.169764+00:00",
# #     "status": "Succeeded",
# #     "synchronizationId": "ba5804ed-a4c9-45ca-9691-e30169c8b361",
# #     "synchronizationMode": "Incremental"
# #   }
# # ]
#         self.cmd('az datashare share-subscription list-synchronization-detail '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscriptions_3}" '
#                  '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
#                  checks=[])

#         self.cmd('az datashare share-subscription cancel-synchronization '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}" '
#                  '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
#                  checks=[])

        sourceDatasets = self.cmd('az datashare consumer-source-dataset list '
                                  '--account-name "{Account2}" '
                                  '--resource-group "{rg2}" '
                                  '--share-subscription-name "{ShareSubscription1}"',
                                  checks=[self.check('[0].dataSetName', '{Dataset1}'),
                                          self.check('[0].dataSetType', 'Container')]).get_output_in_json()
        sourceDatasetId = sourceDatasets[0]['dataSetId']

        storage_account2_json = self.cmd('az storage account show '
                                         '-n {sa2} '
                                         '-g {rg2}').get_output_in_json()

        accountPrincipalId2 = datashareAccount2['identity']['principalId']
        self.cmd('az role assignment create '
                 '--role "Storage Blob Data Contributor" '  # ba92f5b4-2d11-453d-a403-e96b0029c9fe
                 '--assignee-object-id {} '
                 '--assignee-principal-type ServicePrincipal '
                 '--scope {}'.format(accountPrincipalId2, storage_account2_json['id']))

        datasetMappingContent = {"data_set_id": "{}".format(sourceDatasetId),
                                 "container_name": "{}".format(self.kwargs.get('Container2', '')),
                                 "storage_account_name": "{}".format(self.kwargs.get('sa2', '')),
                                 "kind": "BlobFolder",
                                 "prefix": "{}".format(self.kwargs.get('Dataset1', ''))}
        self.kwargs.update({
            'DatasetMappingContent1': datasetMappingContent
        })
        self.cmd('az datashare dataset-mapping create '
                 '--account-name "{Account2}" '
                 '--name "{DatasetMapping1}" '
                 '--resource-group "{rg2}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--mapping "{DatasetMappingContent1}"',
                 checks=[])
# #  {
# #   "containerName": "newcontainer",
# #   "dataSetId": "2036a39f-add6-4347-9c82-a424dfaf4e8d",
# #   "dataSetMappingStatus": "Ok",
# #   "id": "/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/cli_test_datashare_SampleResourceGroup/providers/Microsoft.DataShare/accounts/cli_test_accounts/shareSubscriptions/cli_test_share_subscriptions/dataSetMappings/cli_test_data_set_mappings",
# #   "kind": "BlobFolder",
# #   "name": "cli_test_data_set_mappings",
# #   "prefix": "bootdiagnostic",
# #   "provisioningState": "Succeeded",
# #   "resourceGroup": "cli_test_datashare_SampleResourceGroup",
# #   "storageAccountName": "fengsharedata",
# #   "subscriptionId": "0b1f6471-1bf0-4dda-aec3-cb9272f09590",
# #   "type": "Microsoft.DataShare/DataSetMappings"
# # }

#         self.cmd('az datashare share-subscription synchronize '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}" '
#                  '--synchronization-mode "Incremental"',
#                  checks=[])
# #                  {
# #   "durationMs": null,
# #   "endTime": null,
# #   "message": null,
# #   "startTime": null,
# #   "status": "Queued",
# #   "synchronizationId": "ba5804ed-a4c9-45ca-9691-e30169c8b361",
# #   "synchronizationMode": "Incremental"
# # }

#         self.cmd('az datashare dataset-mapping show '
#                  '--account-name "{Account1}" '
#                  '--name "{DatasetMapping1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}"',
#                  checks=[])

#         self.cmd('az datashare dataset-mapping list '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}"',
#                  checks=[])

#         self.cmd('az datashare share-subscription list-source-share-synchronization-setting '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscriptions_3}"',
#                  checks=[])
# #                  [
# #   {
# #     "kind": "ScheduleBased",
# #     "recurrenceInterval": "Day",
# #     "synchronizationTime": "2020-04-03T08:45:35+00:00"
# #   }
# # ]

# # az datashare trigger create --account-name "cli_test_accounts" --resource-group "cli_test_datashare_SampleResourceGroup" --share-subscription-name "cli_test_share_subscriptions" --name "cli_test_triggers" --trigger "{\"kind\":\"ScheduleBased\",\"recurrenceInterval\":\"Day\",\"synchronizationTime\":\"2020-04-03T08:45:35+00:00\"}"
#         self.cmd('az datashare trigger create '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}" '
#                  '--kind "ScheduleBased" '
#                  '--name "{Trigger1}"',
#                  checks=[])
# #                  {
# #   "id": "/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/cli_test_datashare_SampleResourceGroup/providers/Microsoft.DataShare/accounts/cli_test_accounts/shareSubscriptions/cli_test_share_subscriptions/triggers/cli_test_triggers",
# #   "kind": "Trigger",
# #   "name": "cli_test_triggers",
# #   "properties": {
# #     "createdAt": "2020-04-05T08:13:52.1020699Z",
# #     "provisioningState": "Creating",
# #     "recurrenceInterval": "Day",
# #     "synchronizationMode": "Incremental",
# #     "synchronizationTime": "2020-04-03T08:45:35Z",
# #     "triggerStatus": "Inactive",
# #     "userName": "Feng Zhou"
# #   },
# #   "resourceGroup": "cli_test_datashare_SampleResourceGroup",
# #   "type": "Microsoft.DataShare/Triggers"
# # }

#         self.cmd('az datashare trigger show '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}" '
#                  '--trigger-name "{Trigger1}"',
#                  checks=[])
# # {
# #   "createdAt": "2020-04-05T08:13:52.102069+00:00",
# #   "id": "/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/cli_test_datashare_SampleResourceGroup/providers/Microsoft.DataShare/accounts/cli_test_accounts/shareSubscriptions/cli_test_share_subscriptions/triggers/cli_test_triggers",
# #   "kind": "ScheduleBased",
# #   "name": "cli_test_triggers",
# #   "provisioningState": "Succeeded",
# #   "recurrenceInterval": "Day",
# #   "resourceGroup": "cli_test_datashare_SampleResourceGroup",
# #   "synchronizationMode": "Incremental",
# #   "synchronizationTime": "2020-04-03T08:45:35+00:00",
# #   "triggerStatus": "Active",
# #   "type": "Microsoft.DataShare/Triggers",
# #   "userName": "Feng Zhou"
# # }

#         self.cmd('az datashare trigger list '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}"',
#                  checks=[])

# # Clean up
#         self.cmd('az datashare trigger delete '
#                  '--account-name "{Account1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}" '
#                  '--name "{Trigger1}"',
#                  checks=[])
#         self.cmd('az datashare dataset-mapping delete '
#                  '--account-name "{Account1}" '
#                  '--name "{DatasetMapping1}" '
#                  '--resource-group "{rg}" '
#                  '--share-subscription-name "{ShareSubscription1}"',
#                  checks=[])
        # self.cmd('az datashare share-subscription delete '
        #          '--account-name "{Account1}" '
        #          '--resource-group "{rg}" '
        #          '--name "{ShareSubscription1}"',
        #          checks=[])

        # Provider commands
        self.cmd('az account set -s "{ProviderSubscription}"')
        providerShareSubscriptions = self.cmd('az datashare provider-share-subscription list '
                                              '--account-name "{Account1}" '
                                              '--resource-group "{rg}" '
                                              '--share-name "{Share1}"',
                                              checks=[self.check('[0].consumerEmail', '{ConsumerEmail}'),
                                                      self.check('[0].providerEmail', '{ProviderEmail}'),
                                                      self.check('[0].shareSubscriptionStatus', 'Active'),
                                                      self.check('[0].name', '{ShareSubscription1}')]).get_output_in_json()
        shareSubscriptionObjectId = providerShareSubscriptions[0]['shareSubscriptionObjectId']
        self.kwargs.update({'ProviderShareSubscriptionObjectId': shareSubscriptionObjectId})

        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{Account1}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Active'),
                         self.check('name', '{ShareSubscription1}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        self.cmd('az datashare provider-share-subscription revoke '
                 '--account-name "{Account1}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Revoking'),
                         self.check('name', '{ShareSubscription1}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        if self.is_live or self.in_recording:
            import time
            time.sleep(5)

        self.cmd('az datashare provider-share-subscription reinstate '
                 '--account-name "{Account1}" '
                 '--share-subscription "{ProviderShareSubscriptionObjectId}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[self.check('consumerEmail', '{ConsumerEmail}'),
                         self.check('providerEmail', '{ProviderEmail}'),
                         self.check('shareSubscriptionStatus', 'Active'),
                         self.check('name', '{ShareSubscription1}'),
                         self.check('shareSubscriptionObjectId', '{ProviderShareSubscriptionObjectId}')])

        # Clean up
        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--name "{SynchronizationSettings_2}" '
                 '--yes',
                 checks=[])

        # self.cmd('az datashare invitation delete '
        #          '--account-name "{Account1}" '
        #          '--name "{Invitation1}" '
        #          '--resource-group "{rg}" '
        #          '--share-name "{Share1}"',
        #          checks=[])

        self.cmd('az datashare dataset delete '
                 '--account-name "{Account1}" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--yes',
                 checks=[])

        self.cmd('az datashare delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--name "{Share1}" '
                 '--yes',
                 checks=[])

        self.cmd('az datashare account delete '
                 '--name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--no-wait '
                 '--yes',
                 checks=[])
