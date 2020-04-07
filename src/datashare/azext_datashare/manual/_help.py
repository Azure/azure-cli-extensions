# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['datashare account'] = """
    type: group
    short-summary: Commands to manage datashare accounts
"""

helps['datashare account list'] = """
    type: command
    short-summary: List Accounts in Subscription
    examples:
      - name: Accounts_ListByResourceGroup
        text: |-
               az datashare account list --resource-group MyResourceGroup
"""

helps['datashare account show'] = """
    type: command
    short-summary: Get an account
    examples:
      - name: Accounts_Get
        text: |-
               az datashare account show --name MyAccount --resource-group MyResourceGroup
"""

helps['datashare account create'] = """
    type: command
    short-summary: Create an account
    parameters:
      - name: --identity
        short-summary: Identity of resource.
        long-summary: |
            Usage:   --identity [type=SystemAssigned] [tenantId=VAL principalId=VAL]
    examples:
      - name: Accounts_Create
        text: |-
               az datashare account create --identity type=SystemAssigned --location "West US 2" --tags tag1=Red tag2=White --name MyAccount --resource-group MyResourceGroup
"""

helps['datashare account update'] = """
    type: command
    short-summary: Patch an account
    examples:
      - name: Accounts_Update
        text: |-
               az datashare account update --name MyAccount --tags tag1=Red tag2=White --resource-group MyResourceGroup
"""

helps['datashare account delete'] = """
    type: command
    short-summary: Delete an account
    examples:
      - name: Delete the account
        text: |-
               az datashare account delete --name MyAccount --resource-group MyResourceGroup
"""

helps['datashare account wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare account is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare account is successfully provisioned.
          text: az datashare account wait --name MyAccount --resource-group MyResourceGroup --created
"""

helps['datashare consumer-invitation'] = """
    type: group
    short-summary: Commands for consumers to manage datashare invitations
"""

helps['datashare consumer-invitation list'] = """
    type: command
    short-summary: Lists invitations
    examples:
      - name: ConsumerInvitations_ListInvitations
        text: |-
               az datashare consumer-invitation list
"""

helps['datashare consumer-invitation show'] = """
    type: command
    short-summary: Get an invitation
    examples:
      - name: ConsumerInvitations_Get
        text: |-
               az datashare consumer-invitation show --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
"""

helps['datashare consumer-invitation reject-invitation'] = """
    type: command
    short-summary: Reject an invitation
    examples:
      - name: ConsumerInvitations_RejectInvitation
        text: |-
               az datashare consumer-invitation reject-invitation --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
"""

helps['datashare dataset'] = """
    type: group
    short-summary: Commands for providers to manage datashare datasets
"""

helps['datashare dataset list'] = """
    type: command
    short-summary: List DataSets in a share
    examples:
      - name: DataSets_ListByShare
        text: |-
               az datashare dataset list --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare dataset show'] = """
    type: command
    short-summary: Get a DataSet in a share
    examples:
      - name: DataSets_Get
        text: |-
               az datashare dataset show --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare dataset create'] = """
    type: command
    short-summary: Create a DataSet
    examples:
      - name: DataSets_Create
        text: |-
               az datashare dataset create --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1" \
--dataset "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\": \
\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}"
      - name: DataSets_KustoCluster_Create
        text: |-
               az datashare dataset create --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1" \
--dataset "{\\"kind\\":\\"KustoCluster\\",\\"properties\\":{\\"kustoClusterResourceId\\": \
\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1\\"}}"
      - name: DataSets_KustoDatabase_Create
        text: |-
               az datashare dataset create --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1" \
--dataset "{\\"kind\\":\\"KustoDatabase\\",\\"properties\\":{\\"kustoDatabaseResourceId\\": \
\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\"}}"
      - name: DataSets_SqlDBTable_Create
        text: |-
               az datashare dataset create --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1" \
--dataset "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"databaseName\\":\\"SqlDB1\\",\\"schemaName\\":\\"dbo\\", \
\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\", \
\\"tableName\\":\\"Table1\\"}}"
      - name: DataSets_SqlDWTable_Create
        text: |-
               az datashare dataset create --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1" \
--dataset "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"dataWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\", \
\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\
\\",\\"tableName\\":\\"Table1\\"}}"
"""

helps['datashare dataset delete'] = """
    type: command
    short-summary: Delete a DataSet in a share
    examples:
      - name: DataSets_Delete
        text: |-
               az datashare dataset delete --account-name MyAccount --name "Dataset1" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare dataset wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare dataset is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare dataset is successfully provisioned.
          text: az datashare dataset wait --account-name MyAccount --share-name "Share1" --name "Dataset1" --resource-group MyResourceGroup --created
"""

helps['datashare dataset-mapping'] = """
    type: group
    short-summary: Commands for consumers to manage datashare dataset mappings
"""

helps['datashare dataset-mapping list'] = """
    type: command
    short-summary: List DataSetMappings in a share subscription
    examples:
      - name: DataSetMappings_ListByShareSubscription
        text: |-
               az datashare dataset-mapping list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1"
"""

helps['datashare dataset-mapping show'] = """
    type: command
    short-summary: Get a DataSetMapping in a shareSubscription
    examples:
      - name: DataSetMappings_Get
        text: |-
               az datashare dataset-mapping show --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1"
"""

helps['datashare dataset-mapping create'] = """
    type: command
    short-summary: Create a DataSetMapping
    examples:
      - name: DataSetMappings_Create
        text: |-
               az datashare dataset-mapping create --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" \
--mapping "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\"filePath\
\\":\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}"
      - name: DataSetMappings_SqlDB_Create
        text: |-
               az datashare dataset-mapping create --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" \
--mapping "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\"databaseName\\":\\"Database1\\"\
,\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}"
      - name: DataSetMappings_SqlDWDataSetToAdlsGen2File_Create
        text: |-
               az datashare dataset-mapping create --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" \
--mapping "{\\"kind\\":\\"AdlsGen2File\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\"filePath\\":\\"file21\\",\\"fileSystem\\": \
\\"fileSystem\\",\\"outputType\\":\\"Csv\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}"
      - name: DataSetMappings_SqlDW_Create
        text: |-
               az datashare dataset-mapping create --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" \
--mapping "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\"dataWarehouseName\\":\\"DataWarehouse1\\",\
\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}"
"""

helps['datashare dataset-mapping delete'] = """
    type: command
    short-summary: Delete a DataSetMapping in a shareSubscription
    examples:
      - name: DataSetMappings_Delete
        text: |-
               az datashare dataset-mapping delete --account-name MyAccount --name "DatasetMapping1" --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1"
"""

helps['datashare invitation'] = """
    type: group
    short-summary: Commands for providers to manage datashare invitations
"""

helps['datashare invitation list'] = """
    type: command
    short-summary: List invitations in a share
    examples:
      - name: Invitations_ListByShare
        text: |-
               az datashare invitation list --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare invitation show'] = """
    type: command
    short-summary: Get an invitation in a share
    examples:
      - name: Invitations_Get
        text: |-
               az datashare invitation show --account-name MyAccount --name "Invitation1" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare invitation create'] = """
    type: command
    short-summary: Create an invitation
    examples:
      - name: Invitations_Create
        text: |-
               az datashare invitation create --account-name MyAccount --target-email "receiver@microsoft.com" --name "Invitation1" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare invitation delete'] = """
    type: command
    short-summary: Delete an invitation in a share
    examples:
      - name: Invitations_Delete
        text: |-
               az datashare invitation delete --account-name MyAccount --name "Invitation1" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare'] = """
    type: group
    short-summary: Commands to manage datashare
"""

helps['datashare list'] = """
    type: command
    short-summary: List shares in an account
    examples:
      - name: Shares_ListByAccount
        text: |-
               az datashare list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['datashare show'] = """
    type: command
    short-summary: Get a share
    examples:
      - name: Shares_Get
        text: |-
               az datashare show --account-name MyAccount --resource-group MyResourceGroup --name "Share1"
"""

helps['datashare create'] = """
    type: command
    short-summary: Create a share
    examples:
      - name: Shares_Create
        text: |-
               az datashare create --account-name MyAccount --resource-group MyResourceGroup --description "share description" --share-kind "CopyBased" --terms "Confidential" --name "Share1"
"""

helps['datashare delete'] = """
    type: command
    short-summary: Delete a share
    examples:
      - name: Shares_Delete
        text: |-
               az datashare delete --account-name MyAccount --resource-group MyResourceGroup --name "Share1"
"""

helps['datashare list-synchronization-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: Shares_ListSynchronizationDetails
        text: |-
               az datashare list-synchronization-detail --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare list-synchronization'] = """
    type: command
    short-summary: List synchronizations of a share
    examples:
      - name: Shares_ListSynchronizations
        text: |-
               az datashare list-synchronization --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare is successfully provisioned.
          text: az datashare wait --account-name MyAccount --resource-group MyResourceGroup --name "Share1" --created
"""

helps['datashare provider-share-subscription'] = """
    type: group
    short-summary: Commands for providers to manage datashare share subscriptions
"""

helps['datashare provider-share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in a provider share
    examples:
      - name: ProviderShareSubscriptions_ListByShare
        text: |-
               az datashare provider-share-subscription list --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare provider-share-subscription show'] = """
    type: command
    short-summary: Get share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_GetByShare
        text: |-
               az datashare provider-share-subscription show --account-name MyAccount --share-subscription "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare provider-share-subscription revoke'] = """
    type: command
    short-summary: Revoke share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_Revoke
        text: |-
               az datashare provider-share-subscription revoke --account-name MyAccount --share-subscription "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare provider-share-subscription reinstate'] = """
    type: command
    short-summary: Reinstate share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_Reinstate
        text: |-
               az datashare provider-share-subscription reinstate --account-name MyAccount --share-subscription "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare provider-share-subscription wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare provider share subscription is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare provider share subscription is successfully provisioned.
          text: az datashare provider-share-subscription wait --account-name MyAccount --share-subscription "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group MyResourceGroup --share-name "Share1" --created
"""

helps['datashare share-subscription'] = """
    type: group
    short-summary: Commands for consumers to manage datashare share subscriptions
"""

helps['datashare share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in an account
    examples:
      - name: ShareSubscriptions_ListByAccount
        text: |-
               az datashare share-subscription list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['datashare share-subscription show'] = """
    type: command
    short-summary: Get a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Get
        text: |-
               az datashare share-subscription show --account-name MyAccount --resource-group MyResourceGroup --name "ShareSubscription1"
"""

helps['datashare share-subscription create'] = """
    type: command
    short-summary: Create a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Create
        text: |-
               az datashare share-subscription create --account-name MyAccount --resource-group MyResourceGroup --invitation-id "12345678-1234-1234-12345678abd" --source-share-location "eastus2" --name "ShareSubscription1"
"""

helps['datashare share-subscription delete'] = """
    type: command
    short-summary: Delete a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Delete
        text: |-
               az datashare share-subscription delete --account-name MyAccount --resource-group MyResourceGroup --name "ShareSubscription1"
"""

helps['datashare share-subscription list-synchronization-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: ShareSubscriptions_ListSynchronizationDetails
        text: |-
               az datashare share-subscription list-synchronization-detail --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSub1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare share-subscription synchronize'] = """
    type: command
    short-summary: Initiate a copy
    examples:
      - name: ShareSubscriptions_Synchronize
        text: |-
               az datashare share-subscription synchronize --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --synchronization-mode "Incremental"
"""

helps['datashare share-subscription cancel-synchronization'] = """
    type: command
    short-summary: Request to cancel a synchronization.
    examples:
      - name: ShareSubscriptions_CancelSynchronization
        text: |-
               az datashare share-subscription cancel-synchronization --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare share-subscription list-source-share-synchronization-setting'] = """
    type: command
    short-summary: Get synchronization settings set on a share
    examples:
      - name: ShareSubscriptions_ListSourceShareSynchronizationSettings
        text: |-
               az datashare share-subscription list-source-share-synchronization-setting --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSub1"
"""

helps['datashare share-subscription list-synchronization'] = """
    type: command
    short-summary: List synchronizations of a share subscription
    examples:
      - name: ShareSubscriptions_ListSynchronizations
        text: |-
               az datashare share-subscription list-synchronization --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSub1"
"""

helps['datashare share-subscription wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare share subscription is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare share subscription is successfully provisioned.
          text: az datashare share-subscription wait --account-name MyAccount --resource-group MyResourceGroup --name "ShareSubscription1" --created
"""

helps['datashare consumer-source-dataset'] = """
    type: group
    short-summary: Commands for consumers to manage datashare source datasets
"""

helps['datashare consumer-source-dataset list'] = """
    type: command
    short-summary: Get source dataSets of a shareSubscription
    examples:
      - name: ConsumerSourceDataSets_ListByShareSubscription
        text: |-
               az datashare consumer-source-dataset list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "Share1"
"""

helps['datashare synchronization-setting'] = """
    type: group
    short-summary: Commands for providers to manage datashare synchronization settings
"""

helps['datashare synchronization-setting list'] = """
    type: command
    short-summary: List synchronizationSettings in a share
    examples:
      - name: SynchronizationSettings_ListByShare
        text: |-
               az datashare synchronization-setting list --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1"
"""

helps['datashare synchronization-setting show'] = """
    type: command
    short-summary: Get a synchronizationSetting in a share
    examples:
      - name: SynchronizationSettings_Get
        text: |-
               az datashare synchronization-setting show --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1" --name "SyncrhonizationSetting1"
"""

helps['datashare synchronization-setting create'] = """
    type: command
    short-summary: Create or update a synchronizationSetting
    examples:
      - name: SynchronizationSettings_Create
        text: |-
               az datashare synchronization-setting create --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1" --name "Dataset1" --setting "{\"recurrenceInterval\":\"Day\",\"synchronizationTime\":\"2020-04-05T10:50:00Z\",\"kind\":\"ScheduleBased\"}"
"""

helps['datashare synchronization-setting delete'] = """
    type: command
    short-summary: Delete a synchronizationSetting in a share
    examples:
      - name: SynchronizationSettings_Delete
        text: |-
               az datashare synchronization-setting delete --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1" --name "SyncrhonizationSetting1"
"""

helps['datashare synchronization-setting wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare synchronization setting is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare synchronization setting is successfully provisioned.
          text: az datashare synchronization-setting wait --account-name MyAccount --resource-group MyResourceGroup --share-name "Share1" --name "SyncrhonizationSetting1" --created
"""

helps['datashare trigger'] = """
    type: group
    short-summary: Commands for consumers to manage datashare triggers
"""

helps['datashare trigger list'] = """
    type: command
    short-summary: List Triggers in a share subscription
    examples:
      - name: Triggers_ListByShareSubscription
        text: |-
               az datashare trigger list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1"
"""

helps['datashare trigger show'] = """
    type: command
    short-summary: Get a Trigger in a shareSubscription
    examples:
      - name: Triggers_Get
        text: |-
               az datashare trigger show --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --name "Trigger1"
"""

helps['datashare trigger create'] = """
    type: command
    short-summary: Create a Trigger
    examples:
      - name: Triggers_Create
        text: |-
               az datashare trigger create --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --name "Trigger1" --trigger "{\"kind\":\"ScheduleBased\",\"recurrenceInterval\":\"Day\",\"synchronizationTime\":\"2020-04-03T08:45:35+00:00\"}"
"""

helps['datashare trigger delete'] = """
    type: command
    short-summary: Delete a Trigger in a shareSubscription
    examples:
      - name: Triggers_Delete
        text: |-
               az datashare trigger delete --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --name "Trigger1"
"""

helps['datashare trigger wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare trigger is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare trigger is successfully provisioned.
          text: az datashare trigger wait --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name "ShareSubscription1" --name "Trigger1" --created
"""
