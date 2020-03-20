# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataShareManagementClientScenarioTest(ScenarioTest):

    def current_subscription(self):
        subs = self.cmd('az account show').get_output_in_json()
        return subs['id']

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_SampleResourceGroup'[:9], key='rg')
    def test_datashare(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.current_subscription()
        })

        self.kwargs.update({
            'Account1': self.create_random_name(prefix='cli_test_accounts'[:9], length=24),
            'Share1': self.create_random_name(prefix='cli_test_shares'[:9], length=24),
            'ShareSubscription1': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_2': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_3': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'Dataset1': self.create_random_name(prefix='cli_test_synchronization_settings'[:9], length=24),
            'SynchronizationSettings_2': self.create_random_name(prefix='cli_test_synchronization_settings'[:9],
                                                                 length=24),
            'Trigger1': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
            'Dataset1': self.create_random_name(prefix='cli_test_data_sets'[:9], length=24),
            'DatasetMapping1': self.create_random_name(prefix='cli_test_data_set_mappings'[:9], length=24),
            'Invitation1': self.create_random_name(prefix='cli_test_invitations'[:9], length=24),
        })

        # EXAMPLE: Accounts/resource-group-name/Accounts_Create
        self.cmd('az datashare account create '
                 '--identity type=SystemAssigned '
                 '--location "West US 2" '
                 '--tags tag1=Red tag2=White '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_Create
        self.cmd('az datashare share create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--properties-description "share description" '
                 '--properties-share-kind "CopyBased" '
                 '--properties-terms "Confidential" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/resource-group-name/DataSets_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--data-set "{{\\"kind\\":\\"Blob\\",\\"properties\\":{{\\"containerName\\":\\"C1\\",\\"filePath\\":'
                 '\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",'
                 '\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}}}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/data-set/DataSets_SqlDWTable_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--data-set "{{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{{\\"dataWarehouseName\\":\\"DataWarehouse'
                 '1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/{subscription_id}/resourc'
                 'eGroups/{rg}/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}}}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/data-set/DataSets_SqlDBTable_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--data-set "{{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{{\\"databaseName\\":\\"SqlDB1\\",\\"schem'
                 'aName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/'
                 'providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}}}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/data-set/DataSets_KustoCluster_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--data-set "{{\\"kind\\":\\"KustoCluster\\",\\"properties\\":{{\\"kustoClusterResourceId\\":\\"/subsc'
                 'riptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Kusto/clusters/Cluster1\\"}}}}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/data-set/DataSets_KustoDatabase_Create
        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--data-set "{{\\"kind\\":\\"KustoDatabase\\",\\"properties\\":{{\\"kustoDatabaseResourceId\\":\\"/sub'
                 'scriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Kusto/clusters/Cluster1/database'
                 's/Database1\\"}}}}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_Create
        self.cmd('az datashare share-subscription create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--properties-invitation-id "12345678-1234-1234-12345678abd" '
                 '--properties-source-share-location "eastus2" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: Invitations/resource-group-name/Invitations_Create
        self.cmd('az datashare invitation create '
                 '--account-name "{Account1}" '
                 '--properties-target-email "receiver@microsoft.com" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Create
        self.cmd('az datashare trigger create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger "{{\\"kind\\":\\"ScheduleBased\\",\\"properties\\":{{\\"recurrenceInterval\\":\\"Day\\",\\"'
                 'synchronizationMode\\":\\"Incremental\\",\\"synchronizationTime\\":\\"2018-11-14T04:47:52.9614956Z\\"'
                 '}}}}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        # EXAMPLE: SynchronizationSettings/resource-group-name/SynchronizationSettings_Create
        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-setting "{{\\"kind\\":\\"ScheduleBased\\",\\"properties\\":{{\\"recurrenceInterval'
                 '\\":\\"Day\\",\\"synchronizationTime\\":\\"2018-11-14T04:47:52.9614956Z\\"}}}}" '
                 '--synchronization-setting-name "{Dataset1}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/data-set-mapping/DataSetMappings_SqlDW_Create
        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--data-set-mapping "{{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{{\\"dataSetId\\":\\"a08f184b-0567'
                 '-4b11-ba22-a1199336d226\\",\\"dataWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\",\\'
                 '"sqlServerResourceId\\":\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.S'
                 'ql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}}}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/data-set-mapping/DataSetMappings_SqlDB_Create
        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--data-set-mapping "{{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{{\\"dataSetId\\":\\"a08f184b-0567'
                 '-4b11-ba22-a1199336d226\\",\\"databaseName\\":\\"Database1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServer'
                 'ResourceId\\":\\"/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.Sql/servers'
                 '/Server1\\",\\"tableName\\":\\"Table1\\"}}}}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/data-set-mapping/DataSetMappings_SqlDWDataSetToAdlsGen2File_Create
        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--data-set-mapping "{{\\"kind\\":\\"AdlsGen2File\\",\\"properties\\":{{\\"dataSetId\\":\\"a08f184b-05'
                 '67-4b11-ba22-a1199336d226\\",\\"filePath\\":\\"file21\\",\\"fileSystem\\":\\"fileSystem\\",\\"outputT'
                 'ype\\":\\"Csv\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\'
                 '",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}}}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/resource-group-name/DataSetMappings_Create
        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--data-set-mapping "{{\\"kind\\":\\"Blob\\",\\"properties\\":{{\\"containerName\\":\\"C1\\",\\"dataSe'
                 'tId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\":\\"'
                 'SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-'
                 '4e77-ad86-90acdc75eb1a\\"}}}}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/resource-group-name/DataSetMappings_Get
        self.cmd('az datashare data-set-mapping show '
                 '--account-name "{Account1}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: ProviderShareSubscriptions/resource-group-name/ProviderShareSubscriptions_GetByShare
        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: SynchronizationSettings/resource-group-name/SynchronizationSettings_Get
        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-setting-name "{SynchronizationSettings_2}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Get
        self.cmd('az datashare trigger show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        # EXAMPLE: Invitations/resource-group-name/Invitations_Get
        self.cmd('az datashare invitation show '
                 '--account-name "{Account1}" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_Get
        self.cmd('az datashare share-subscription show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSets/resource-group-name/DataSets_Get
        self.cmd('az datashare data-set show '
                 '--account-name "{Account1}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_Get
        self.cmd('az datashare share show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Accounts/resource-group-name/Accounts_Get
        self.cmd('az datashare account show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: ConsumerInvitations/location/ConsumerInvitations_Get
        self.cmd('az datashare consumer-invitation show '
                 '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        # EXAMPLE: ConsumerSourceDataSets/resource-group-name/ConsumerSourceDataSets_ListByShareSubscription
        self.cmd('az datashare consumer-source-data-set list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_2}"',
                 checks=[])

        # EXAMPLE: DataSetMappings/resource-group-name/DataSetMappings_ListByShareSubscription
        self.cmd('az datashare data-set-mapping list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_ListByShareSubscription
        self.cmd('az datashare trigger list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: ProviderShareSubscriptions/resource-group-name/ProviderShareSubscriptions_ListByShare
        self.cmd('az datashare provider-share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: SynchronizationSettings/resource-group-name/SynchronizationSettings_ListByShare
        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Invitations/resource-group-name/Invitations_ListByShare
        self.cmd('az datashare invitation list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: DataSets/resource-group-name/DataSets_ListByShare
        self.cmd('az datashare data-set list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_ListByAccount
        self.cmd('az datashare share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_ListByAccount
        self.cmd('az datashare share list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Accounts/resource-group-name/Accounts_ListByResourceGroup
        self.cmd('az datashare account list '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: Accounts/skip-token/Accounts_ListBySubscription
        self.cmd('az datashare account list',
                 checks=[])

        # EXAMPLE: ConsumerInvitations/skip-token/ConsumerInvitations_ListInvitations
        self.cmd('az datashare consumer-invitation list',
                 checks=[])

        # EXAMPLE: ProviderShareSubscriptions/resource-group-name/ProviderShareSubscriptions_Reinstate
        self.cmd('az datashare provider-share-subscription reinstate '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ProviderShareSubscriptions/resource-group-name/ProviderShareSubscriptions_Revoke
        self.cmd('az datashare provider-share-subscription revoke '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_ListSourceShareSynchronizationSettings
        self.cmd('az datashare share-subscription list-source-share-synchronization-setting '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_ListSynchronizationDetails
        self.cmd('az datashare share-subscription list-synchronization-detail '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_CancelSynchronization
        self.cmd('az datashare share-subscription cancel-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_ListSynchronizations
        self.cmd('az datashare share-subscription list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_Synchronize
        self.cmd('az datashare share-subscription synchronize '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--synchronization-mode "Incremental"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_ListSynchronizationDetails
        self.cmd('az datashare share list-synchronization-detail '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_ListSynchronizations
        self.cmd('az datashare share list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Accounts/resource-group-name/Accounts_Update
        self.cmd('az datashare account update '
                 '--account-name "{Account1}" '
                 '--tags tag1=Red tag2=White '
                 '--resource-group "{rg}"',
                 checks=[])

        # EXAMPLE: ConsumerInvitations/location/ConsumerInvitations_RejectInvitation
        self.cmd('az datashare consumer-invitation reject-invitation '
                 '--properties-invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        # EXAMPLE: DataSetMappings/resource-group-name/DataSetMappings_Delete
        self.cmd('az datashare data-set-mapping delete '
                 '--account-name "{Account1}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: SynchronizationSettings/resource-group-name/SynchronizationSettings_Delete
        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-setting-name "{SynchronizationSettings_2}"',
                 checks=[])

        # EXAMPLE: Triggers/resource-group-name/Triggers_Delete
        self.cmd('az datashare trigger delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        # EXAMPLE: Invitations/resource-group-name/Invitations_Delete
        self.cmd('az datashare invitation delete '
                 '--account-name "{Account1}" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: ShareSubscriptions/resource-group-name/ShareSubscriptions_Delete
        self.cmd('az datashare share-subscription delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        # EXAMPLE: DataSets/resource-group-name/DataSets_Delete
        self.cmd('az datashare data-set delete '
                 '--account-name "{Account1}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Shares/resource-group-name/Shares_Delete
        self.cmd('az datashare share delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        # EXAMPLE: Accounts/resource-group-name/Accounts_Delete
        self.cmd('az datashare account delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])
