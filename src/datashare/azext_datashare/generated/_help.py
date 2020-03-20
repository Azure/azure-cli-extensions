# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['datashare account'] = """
    type: group
    short-summary: datashare account
"""

helps['datashare account list'] = """
    type: command
    short-summary: List Accounts in Subscription
    examples:
      - name: Accounts_ListByResourceGroup
        text: |-
               az datashare account list --resource-group "SampleResourceGroup"
"""

helps['datashare account show'] = """
    type: command
    short-summary: Get an account
    examples:
      - name: Accounts_Get
        text: |-
               az datashare account show --account-name "Account1" --resource-group
               "SampleResourceGroup"
"""

helps['datashare account create'] = """
    type: command
    short-summary: Create an account
    examples:
      - name: Accounts_Create
        text: |-
               az datashare account create --identity type=SystemAssigned --location "West US 2" --tags
               tag1=Red tag2=White --account-name "Account1" --resource-group "SampleResourceGroup"
"""

helps['datashare account update'] = """
    type: command
    short-summary: Patch an account
    examples:
      - name: Accounts_Update
        text: |-
               az datashare account update --account-name "Account1" --tags tag1=Red tag2=White
               --resource-group "SampleResourceGroup"
"""

helps['datashare account delete'] = """
    type: command
    short-summary: DeleteAccount
    examples:
      - name: Accounts_Delete
        text: |-
               az datashare account delete --account-name "Account1" --resource-group
               "SampleResourceGroup"
"""

helps['datashare consumer-invitation'] = """
    type: group
    short-summary: datashare consumer-invitation
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
               az datashare consumer-invitation show --invitation-id
               "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
"""

helps['datashare consumer-invitation reject-invitation'] = """
    type: command
    short-summary: Reject an invitation
    examples:
      - name: ConsumerInvitations_RejectInvitation
        text: |-
               az datashare consumer-invitation reject-invitation --properties-invitation-id
               "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
"""

helps['datashare data-set'] = """
    type: group
    short-summary: datashare data-set
"""

helps['datashare data-set list'] = """
    type: command
    short-summary: List DataSets in a share
    examples:
      - name: DataSets_ListByShare
        text: |-
               az datashare data-set list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare data-set show'] = """
    type: command
    short-summary: Get a DataSet in a share
    examples:
      - name: DataSets_Get
        text: |-
               az datashare data-set show --account-name "Account1" --data-set-name "Dataset1"
               --resource-group "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare data-set create'] = """
    type: command
    short-summary: Create a DataSet
    examples:
      - name: DataSets_Create
        text: |-
               az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"Blob\\",\\"pr
               operties\\":{\\"containerName\\":\\"C1\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\":\\"SampleRes
               ourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-a
               d86-90acdc75eb1a\\"}}" --data-set-name "Dataset1" --resource-group "SampleResourceGroup"
               --share-name "Share1"
      - name: DataSets_KustoCluster_Create
        text: |-
               az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"KustoCluste
               r\\",\\"properties\\":{\\"kustoClusterResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90
               acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1\\
               "}}" --data-set-name "Dataset1" --resource-group "SampleResourceGroup" --share-name
               "Share1"
      - name: DataSets_KustoDatabase_Create
        text: |-
               az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"KustoDataba
               se\\",\\"properties\\":{\\"kustoDatabaseResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-
               90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster
               1/databases/Database1\\"}}" --data-set-name "Dataset1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
      - name: DataSets_SqlDBTable_Create
        text: |-
               az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"SqlDBTable\\
               ",\\"properties\\":{\\"databaseName\\":\\"SqlDB1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId
               \\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGrou
               p/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}" --data-set-name
               "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1"
      - name: DataSets_SqlDWTable_Create
        text: |-
               az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"SqlDWTable\\
               ",\\"properties\\":{\\"dataWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\",\\"sqlSer
               verResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/Sampl
               eResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}"
               --data-set-name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare data-set delete'] = """
    type: command
    short-summary: Delete a DataSet in a share
    examples:
      - name: DataSets_Delete
        text: |-
               az datashare data-set delete --account-name "Account1" --data-set-name "Dataset1"
               --resource-group "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare data-set-mapping'] = """
    type: group
    short-summary: datashare data-set-mapping
"""

helps['datashare data-set-mapping list'] = """
    type: command
    short-summary: List DataSetMappings in a share subscription
    examples:
      - name: DataSetMappings_ListByShareSubscription
        text: |-
               az datashare data-set-mapping list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
"""

helps['datashare data-set-mapping show'] = """
    type: command
    short-summary: Get a DataSetMapping in a shareSubscription
    examples:
      - name: DataSetMappings_Get
        text: |-
               az datashare data-set-mapping show --account-name "Account1" --data-set-mapping-name
               "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name
               "ShareSubscription1"
"""

helps['datashare data-set-mapping create'] = """
    type: command
    short-summary: Create a DataSetMapping
    examples:
      - name: DataSetMappings_Create
        text: |-
               az datashare data-set-mapping create --account-name "Account1" --data-set-mapping "{\\"kind
               \\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"dataSetId\\":\\"a08f184b-0567-4b11-ba
               22-a1199336d226\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"stor
               ageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}
               }" --data-set-mapping-name "DatasetMapping1" --resource-group "SampleResourceGroup"
               --share-subscription-name "ShareSubscription1"
      - name: DataSetMappings_SqlDB_Create
        text: |-
               az datashare data-set-mapping create --account-name "Account1" --data-set-mapping "{\\"kind
               \\":\\"SqlDBTable\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\
               "databaseName\\":\\"Database1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscripti
               ons/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Micr
               osoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}" --data-set-mapping-name
               "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name
               "ShareSubscription1"
      - name: DataSetMappings_SqlDWDataSetToAdlsGen2File_Create
        text: |-
               az datashare data-set-mapping create --account-name "Account1" --data-set-mapping "{\\"kind
               \\":\\"AdlsGen2File\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\"
               ,\\"filePath\\":\\"file21\\",\\"fileSystem\\":\\"fileSystem\\",\\"outputType\\":\\"Csv\\",\\"resourceGr
               oup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"433
               a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}" --data-set-mapping-name "DatasetMapping1"
               --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
      - name: DataSetMappings_SqlDW_Create
        text: |-
               az datashare data-set-mapping create --account-name "Account1" --data-set-mapping "{\\"kind
               \\":\\"SqlDWTable\\",\\"properties\\":{\\"dataSetId\\":\\"a08f184b-0567-4b11-ba22-a1199336d226\\",\\
               "dataWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/
               subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/prov
               iders/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}" --data-set-mapping-name
               "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name
               "ShareSubscription1"
"""

helps['datashare data-set-mapping delete'] = """
    type: command
    short-summary: Delete a DataSetMapping in a shareSubscription
    examples:
      - name: DataSetMappings_Delete
        text: |-
               az datashare data-set-mapping delete --account-name "Account1" --data-set-mapping-name
               "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name
               "ShareSubscription1"
"""

helps['datashare invitation'] = """
    type: group
    short-summary: datashare invitation
"""

helps['datashare invitation list'] = """
    type: command
    short-summary: List invitations in a share
    examples:
      - name: Invitations_ListByShare
        text: |-
               az datashare invitation list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare invitation show'] = """
    type: command
    short-summary: Get an invitation in a share
    examples:
      - name: Invitations_Get
        text: |-
               az datashare invitation show --account-name "Account1" --invitation-name "Invitation1"
               --resource-group "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare invitation create'] = """
    type: command
    short-summary: Create an invitation
    examples:
      - name: Invitations_Create
        text: |-
               az datashare invitation create --account-name "Account1" --properties-target-email
               "receiver@microsoft.com" --invitation-name "Invitation1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare invitation delete'] = """
    type: command
    short-summary: Delete an invitation in a share
    examples:
      - name: Invitations_Delete
        text: |-
               az datashare invitation delete --account-name "Account1" --invitation-name "Invitation1"
               --resource-group "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare share'] = """
    type: group
    short-summary: datashare share
"""

helps['datashare share list'] = """
    type: command
    short-summary: List shares in an account
    examples:
      - name: Shares_ListByAccount
        text: |-
               az datashare share list --account-name "Account1" --resource-group "SampleResourceGroup"
"""

helps['datashare share show'] = """
    type: command
    short-summary: Get a share
    examples:
      - name: Shares_Get
        text: |-
               az datashare share show --account-name "Account1" --resource-group "SampleResourceGroup"
               --share-name "Share1"
"""

helps['datashare share create'] = """
    type: command
    short-summary: Create a share
    examples:
      - name: Shares_Create
        text: |-
               az datashare share create --account-name "Account1" --resource-group
               "SampleResourceGroup" --properties-description "share description"
               --properties-share-kind "CopyBased" --properties-terms "Confidential" --share-name
               "Share1"
"""

helps['datashare share delete'] = """
    type: command
    short-summary: Delete a share
    examples:
      - name: Shares_Delete
        text: |-
               az datashare share delete --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare share list-synchronization'] = """
    type: command
    short-summary: List synchronizations of a share
    examples:
      - name: Shares_ListSynchronizations
        text: |-
               az datashare share list-synchronization --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare share list-synchronization-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: Shares_ListSynchronizationDetails
        text: |-
               az datashare share list-synchronization-detail --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1" --synchronization-id
               "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare provider-share-subscription'] = """
    type: group
    short-summary: datashare provider-share-subscription
"""

helps['datashare provider-share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in a provider share
    examples:
      - name: ProviderShareSubscriptions_ListByShare
        text: |-
               az datashare provider-share-subscription list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare provider-share-subscription show'] = """
    type: command
    short-summary: Get share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_GetByShare
        text: |-
               az datashare provider-share-subscription show --account-name "Account1"
               --provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare provider-share-subscription revoke'] = """
    type: command
    short-summary: Revoke share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_Revoke
        text: |-
               az datashare provider-share-subscription revoke --account-name "Account1"
               --provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare provider-share-subscription reinstate'] = """
    type: command
    short-summary: Reinstate share subscription in a provider share
    examples:
      - name: ProviderShareSubscriptions_Reinstate
        text: |-
               az datashare provider-share-subscription reinstate --account-name "Account1"
               --provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare share-subscription'] = """
    type: group
    short-summary: datashare share-subscription
"""

helps['datashare share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in an account
    examples:
      - name: ShareSubscriptions_ListByAccount
        text: |-
               az datashare share-subscription list --account-name "Account1" --resource-group
               "SampleResourceGroup"
"""

helps['datashare share-subscription show'] = """
    type: command
    short-summary: Get a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Get
        text: |-
               az datashare share-subscription show --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
"""

helps['datashare share-subscription create'] = """
    type: command
    short-summary: Create a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Create
        text: |-
               az datashare share-subscription create --account-name "Account1" --resource-group
               "SampleResourceGroup" --properties-invitation-id "12345678-1234-1234-12345678abd"
               --properties-source-share-location "eastus2" --share-subscription-name
               "ShareSubscription1"
"""

helps['datashare share-subscription delete'] = """
    type: command
    short-summary: Delete a shareSubscription in an account
    examples:
      - name: ShareSubscriptions_Delete
        text: |-
               az datashare share-subscription delete --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
"""

helps['datashare share-subscription list-source-share-synchronization-setting'] = """
    type: command
    short-summary: Get synchronization settings set on a share
    examples:
      - name: ShareSubscriptions_ListSourceShareSynchronizationSettings
        text: |-
               az datashare share-subscription list-source-share-synchronization-setting --account-name
               "Account1" --resource-group "SampleResourceGroup" --share-subscription-name "ShareSub1"
"""

helps['datashare share-subscription list-synchronization'] = """
    type: command
    short-summary: List synchronizations of a share subscription
    examples:
      - name: ShareSubscriptions_ListSynchronizations
        text: |-
               az datashare share-subscription list-synchronization --account-name "Account1"
               --resource-group "SampleResourceGroup" --share-subscription-name "ShareSub1"
"""

helps['datashare share-subscription list-synchronization-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: ShareSubscriptions_ListSynchronizationDetails
        text: |-
               az datashare share-subscription list-synchronization-detail --account-name "Account1"
               --resource-group "SampleResourceGroup" --share-subscription-name "ShareSub1"
               --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare share-subscription synchronize'] = """
    type: command
    short-summary: Initiate a copy
    examples:
      - name: ShareSubscriptions_Synchronize
        text: |-
               az datashare share-subscription synchronize --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
               --synchronization-mode "Incremental"
"""

helps['datashare share-subscription cancel-synchronization'] = """
    type: command
    short-summary: Request to cancel a synchronization.
    examples:
      - name: ShareSubscriptions_CancelSynchronization
        text: |-
               az datashare share-subscription cancel-synchronization --account-name "Account1"
               --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
               --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
"""

helps['datashare consumer-source-data-set'] = """
    type: group
    short-summary: datashare consumer-source-data-set
"""

helps['datashare consumer-source-data-set list'] = """
    type: command
    short-summary: Get source dataSets of a shareSubscription
    examples:
      - name: ConsumerSourceDataSets_ListByShareSubscription
        text: |-
               az datashare consumer-source-data-set list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "Share1"
"""

helps['datashare synchronization-setting'] = """
    type: group
    short-summary: datashare synchronization-setting
"""

helps['datashare synchronization-setting list'] = """
    type: command
    short-summary: List synchronizationSettings in a share
    examples:
      - name: SynchronizationSettings_ListByShare
        text: |-
               az datashare synchronization-setting list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1"
"""

helps['datashare synchronization-setting show'] = """
    type: command
    short-summary: Get a synchronizationSetting in a share
    examples:
      - name: SynchronizationSettings_Get
        text: |-
               az datashare synchronization-setting show --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1" --synchronization-setting-name
               "SyncrhonizationSetting1"
"""

helps['datashare synchronization-setting create'] = """
    type: command
    short-summary: Create or update a synchronizationSetting
    examples:
      - name: SynchronizationSettings_Create
        text: |-
               az datashare synchronization-setting create --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1" --synchronization-setting "{\\"kind\\":\\"Schedul
               eBased\\",\\"properties\\":{\\"recurrenceInterval\\":\\"Day\\",\\"synchronizationTime\\":\\"2018-11-
               14T04:47:52.9614956Z\\"}}" --synchronization-setting-name "Dataset1"
"""

helps['datashare synchronization-setting delete'] = """
    type: command
    short-summary: Delete a synchronizationSetting in a share
    examples:
      - name: SynchronizationSettings_Delete
        text: |-
               az datashare synchronization-setting delete --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-name "Share1" --synchronization-setting-name
               "SyncrhonizationSetting1"
"""

helps['datashare trigger'] = """
    type: group
    short-summary: datashare trigger
"""

helps['datashare trigger list'] = """
    type: command
    short-summary: List Triggers in a share subscription
    examples:
      - name: Triggers_ListByShareSubscription
        text: |-
               az datashare trigger list --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
"""

helps['datashare trigger show'] = """
    type: command
    short-summary: Get a Trigger in a shareSubscription
    examples:
      - name: Triggers_Get
        text: |-
               az datashare trigger show --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1" --trigger-name
               "Trigger1"
"""

helps['datashare trigger create'] = """
    type: command
    short-summary: Create a Trigger
    examples:
      - name: Triggers_Create
        text: |-
               az datashare trigger create --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1" --trigger "{\\"kind\\":
               \\"ScheduleBased\\",\\"properties\\":{\\"recurrenceInterval\\":\\"Day\\",\\"synchronizationMode\\":\\
               "Incremental\\",\\"synchronizationTime\\":\\"2018-11-14T04:47:52.9614956Z\\"}}" --trigger-name
               "Trigger1"
"""

helps['datashare trigger delete'] = """
    type: command
    short-summary: Delete a Trigger in a shareSubscription
    examples:
      - name: Triggers_Delete
        text: |-
               az datashare trigger delete --account-name "Account1" --resource-group
               "SampleResourceGroup" --share-subscription-name "ShareSubscription1" --trigger-name
               "Trigger1"
"""
