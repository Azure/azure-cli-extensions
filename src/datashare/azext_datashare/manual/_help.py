# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['datashare consumer'] = """
    type: group
    short-summary: Commands for consumers to manage datashare
"""

helps['datashare account'] = """
    type: group
    short-summary: Commands to manage datashare accounts
"""

helps['datashare account list'] = """
    type: command
    short-summary: List datashare accounts
    examples:
      - name: List accounts by resource group
        text: |-
               az datashare account list --resource-group MyResourceGroup
"""

helps['datashare account show'] = """
    type: command
    short-summary: Show an account
    examples:
      - name: Show account information
        text: |-
               az datashare account show --name MyAccount --resource-group MyResourceGroup
"""

helps['datashare account create'] = """
    type: command
    short-summary: Create an account
    examples:
      - name: Create an account
        text: |-
               az datashare account create --location "West US 2" --tags tag1=Red tag2=White --name MyAccount --resource-group MyResourceGroup
"""

helps['datashare account update'] = """
    type: command
    short-summary: Patch an account
    examples:
      - name: Update account tags
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

helps['datashare consumer invitation'] = """
    type: group
    short-summary: Commands for consumers to manage datashare invitations
"""

helps['datashare consumer invitation list'] = """
    type: command
    short-summary: List received invitations
    examples:
      - name: List invitations
        text: |-
               az datashare consumer invitation list
"""

helps['datashare consumer invitation show'] = """
    type: command
    short-summary: Show a received invitation
    examples:
      - name: Show an invitation
        text: |-
               az datashare consumer invitation show --invitation-id 00000000-0000-0000-0000-000000000000 --location "East US 2"
"""

helps['datashare consumer invitation reject'] = """
    type: command
    short-summary: Reject an invitation
    examples:
      - name: Reject an invitation
        text: |-
               az datashare consumer invitation reject --invitation-id 00000000-0000-0000-0000-000000000000 --location "East US 2"
"""

helps['datashare dataset'] = """
    type: group
    short-summary: Commands for providers to manage datashare datasets
"""

helps['datashare dataset list'] = """
    type: command
    short-summary: List datasets in a share
    examples:
      - name: List datasets
        text: |-
               az datashare dataset list --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare dataset show'] = """
    type: command
    short-summary: Show a dataset
    examples:
      - name: Show a dataset
        text: |-
               az datashare dataset show --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare dataset create'] = """
    type: command
    short-summary: Create a dataset
    examples:
      - name: Create a Blob dataset
        text: |-
               az datashare dataset create --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare \
--dataset "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\": \
\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"00000000-0000-0000-0000-000000000000\\"}}"
      - name: Create a KustoCluster dataset
        text: |-
               az datashare dataset create --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare \
--dataset "{\\"kind\\":\\"KustoCluster\\",\\"properties\\":{\\"kustoClusterResourceId\\": \
\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1\\"}}"
      - name: Create a KustoDatabase dataset
        text: |-
               az datashare dataset create --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare \
--dataset "{\\"kind\\":\\"KustoDatabase\\",\\"properties\\":{\\"kustoDatabaseResourceId\\": \
\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/SampleResourceGroup/providers/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\"}}"
      - name: Create a SqlDBTable dataset
        text: |-
               az datashare dataset create --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare \
--dataset "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"databaseName\\":\\"MySqlDB\\",\\"schemaName\\":\\"dbo\\", \
\\"sqlServerResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\", \
\\"tableName\\":\\"Table1\\"}}"
      - name: Create a SqlDWTable dataset
        text: |-
               az datashare dataset create --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare \
--dataset "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"dataWarehouseName\\":\\"MyDataWarehouse\\",\\"schemaName\\":\\"dbo\\", \
\\"sqlServerResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyResourceGroup/providers/Microsoft.Sql/servers/MyServer\
\\",\\"tableName\\":\\"MyTable\\"}}"
"""

helps['datashare dataset delete'] = """
    type: command
    short-summary: Delete a dataset in a share
    examples:
      - name: Delete a dataset
        text: |-
               az datashare dataset delete --account-name MyAccount --name MyDataset --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare dataset wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare dataset is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare dataset is successfully provisioned.
          text: az datashare dataset wait --account-name MyAccount --share-name MyShare --name MyDataset --resource-group MyResourceGroup --created
"""

helps['datashare consumer dataset-mapping'] = """
    type: group
    short-summary: Commands for consumers to manage datashare dataset mappings
"""

helps['datashare consumer dataset-mapping list'] = """
    type: command
    short-summary: List dataset mappings in a share subscription
    examples:
      - name: List dataset mappings
        text: |-
               az datashare consumer dataset-mapping list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription
"""

helps['datashare consumer dataset-mapping show'] = """
    type: command
    short-summary: Show a dataset mapping in a share subscription
    examples:
      - name: Show a dataset mapping
        text: |-
               az datashare consumer dataset-mapping show --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription
"""

helps['datashare consumer dataset-mapping create'] = """
    type: command
    short-summary: Create a dataSet mapping
    examples:
      - name: Create a Blob dataset mapping
        text: |-
               az datashare consumer dataset-mapping create --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription \
--mapping "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containerName\\":\\"C1\\",\\"dataSetId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"filePath\
\\":\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"00000000-0000-0000-0000-000000000000\\"}}"
      - name: Create a SqlDBTable dataset mapping
        text: |-
               az datashare consumer dataset-mapping create --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription \
--mapping "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"dataSetId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"databaseName\\":\\"Database1\\"\
,\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}"
      - name: Create a AdlsGen2File dataset mapping
        text: |-
               az datashare consumer dataset-mapping create --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription \
--mapping "{\\"kind\\":\\"AdlsGen2File\\",\\"properties\\":{\\"dataSetId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"filePath\\":\\"file21\\",\\"fileSystem\\": \
\\"fileSystem\\",\\"outputType\\":\\"Csv\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\"storage2\\",\\"subscriptionId\\":\\"00000000-0000-0000-0000-000000000000\\"}}"
      - name: Create a SqlDWTable dataset mapping
        text: |-
               az datashare consumer dataset-mapping create --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription \
--mapping "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"dataSetId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"dataWarehouseName\\":\\"DataWarehouse1\\",\
\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\\"}}"
"""

helps['datashare consumer dataset-mapping delete'] = """
    type: command
    short-summary: Delete a dataset mapping in a share subscription
    examples:
      - name: Delete a dataset mapping
        text: |-
               az datashare consumer dataset-mapping delete --account-name MyAccount --name MyDatasetMapping --resource-group MyResourceGroup --share-subscription-name MyShareSubscription
"""

helps['datashare invitation'] = """
    type: group
    short-summary: Commands for providers to manage datashare invitations
"""

helps['datashare invitation list'] = """
    type: command
    short-summary: List invitations in a share
    examples:
      - name: List invitations
        text: |-
               az datashare invitation list --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare invitation show'] = """
    type: command
    short-summary: Show an invitation in a share
    examples:
      - name: Show an invitation
        text: |-
               az datashare invitation show --account-name MyAccount --name MyInvitation --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare invitation create'] = """
    type: command
    short-summary: Create an invitation
    examples:
      - name: Create an invitation
        text: |-
               az datashare invitation create --account-name MyAccount --target-email "receiver@microsoft.com" --name MyInvitation --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare invitation delete'] = """
    type: command
    short-summary: Delete an invitation in a share
    examples:
      - name: Delete an invitation
        text: |-
               az datashare invitation delete --account-name MyAccount --name MyInvitation --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare'] = """
    type: group
    short-summary: Commands to manage datashare
"""

helps['datashare list'] = """
    type: command
    short-summary: List datashares in an account
    examples:
      - name: List datashares
        text: |-
               az datashare list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['datashare show'] = """
    type: command
    short-summary: Show a datashare
    examples:
      - name: Show a datashare
        text: |-
               az datashare show --account-name MyAccount --resource-group MyResourceGroup --name MyShare
"""

helps['datashare create'] = """
    type: command
    short-summary: Create a datashare
    examples:
      - name: Create a datashare
        text: |-
               az datashare create --account-name MyAccount --resource-group MyResourceGroup --description "share description" --share-kind "CopyBased" --terms "Confidential" --name MyShare
"""

helps['datashare delete'] = """
    type: command
    short-summary: Delete a datashare
    examples:
      - name: Delete a datashare
        text: |-
               az datashare delete --account-name MyAccount --resource-group MyResourceGroup --name MyShare
"""

helps['datashare synchronization'] = """
    type: group
    short-summary: Commands to manage datashare synchronization
"""

helps['datashare synchronization list-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: List synchronization details
        text: |-
               az datashare synchronization list-detail --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare --synchronization-id 00000000-0000-0000-0000-000000000000
"""

helps['datashare synchronization list'] = """
    type: command
    short-summary: List synchronizations of a datashare
    examples:
      - name: List synchronizations
        text: |-
               az datashare synchronization list --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare is successfully provisioned.
          text: az datashare wait --account-name MyAccount --resource-group MyResourceGroup --name MyShare --created
"""

helps['datashare provider-share-subscription'] = """
    type: group
    short-summary: Commands for providers to manage datashare share subscriptions
"""

helps['datashare provider-share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in a provider share
    examples:
      - name: List share subscriptions
        text: |-
               az datashare provider-share-subscription list --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare provider-share-subscription show'] = """
    type: command
    short-summary: Show a share subscription in a provider share
    examples:
      - name: Show a share subscription
        text: |-
               az datashare provider-share-subscription show --account-name MyAccount --share-subscription 00000000-0000-0000-0000-000000000000 --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare provider-share-subscription revoke'] = """
    type: command
    short-summary: Revoke a share subscription in a provider share
    examples:
      - name: Revoke a share subscription
        text: |-
               az datashare provider-share-subscription revoke --account-name MyAccount --share-subscription 00000000-0000-0000-0000-000000000000 --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare provider-share-subscription reinstate'] = """
    type: command
    short-summary: Reinstate a share subscription in a provider share
    examples:
      - name: Reinstate a share subscription
        text: |-
               az datashare provider-share-subscription reinstate --account-name MyAccount --share-subscription 00000000-0000-0000-0000-000000000000 --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare provider-share-subscription wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare provider share subscription is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare provider share subscription is successfully provisioned.
          text: az datashare provider-share-subscription wait --account-name MyAccount --share-subscription 00000000-0000-0000-0000-000000000000 --resource-group MyResourceGroup --share-name MyShare --created
"""

helps['datashare consumer share-subscription'] = """
    type: group
    short-summary: Commands for consumers to manage datashare share subscriptions
"""

helps['datashare consumer share-subscription list'] = """
    type: command
    short-summary: List share subscriptions in an account
    examples:
      - name: List share subscriptions
        text: |-
               az datashare consumer share-subscription list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['datashare consumer share-subscription show'] = """
    type: command
    short-summary: Show a share subscription in an account
    examples:
      - name: Show a share subscription
        text: |-
               az datashare consumer share-subscription show --account-name MyAccount --resource-group MyResourceGroup --name MyShareSubscription
"""

helps['datashare consumer share-subscription create'] = """
    type: command
    short-summary: Create a share subscription in an account
    examples:
      - name: Create a share subscription
        text: |-
               az datashare consumer share-subscription create --account-name MyAccount --resource-group MyResourceGroup --invitation-id 00000000-0000-0000-0000-000000000000 --source-share-location "eastus2" --name MyShareSubscription
"""

helps['datashare consumer share-subscription delete'] = """
    type: command
    short-summary: Delete a share subscription in an account
    examples:
      - name: Delete a share subscription
        text: |-
               az datashare consumer share-subscription delete --account-name MyAccount --resource-group MyResourceGroup --name MyShareSubscription
"""

helps['datashare consumer share-subscription synchronization'] = """
    type: group
    short-summary: Commands for consumers to manage datashare share subscription synchronizations
"""

helps['datashare consumer share-subscription synchronization list-detail'] = """
    type: command
    short-summary: List synchronization details
    examples:
      - name: List synchronization details
        text: |-
               az datashare consumer share-subscription synchronization list-detail --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSub --synchronization-id 00000000-0000-0000-0000-000000000000
"""

helps['datashare consumer share-subscription synchronization start'] = """
    type: command
    short-summary: Initiate a dataset synchronization
    examples:
      - name: Initiate a dataset synchronization
        text: |-
               az datashare consumer share-subscription synchronization start --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --synchronization-mode "Incremental"
"""

helps['datashare consumer share-subscription synchronization cancel'] = """
    type: command
    short-summary: Request to cancel a synchronization.
    examples:
      - name: Request to cancel a synchronization
        text: |-
               az datashare consumer share-subscription synchronization cancel --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --synchronization-id 00000000-0000-0000-0000-000000000000
"""

helps['datashare consumer share-subscription synchronization wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare share subscription synchronization is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare share subscription synchronization finishes successfully.
          text: az datashare consumer share-subscription synchronization wait --custom "status=='Succeeded'" --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --synchronization-id 00000000-0000-0000-0000-000000000000
        - name: Pause executing next line of CLI script until the datashare share subscription synchronization is cancelled.
          text: az datashare consumer share-subscription synchronization wait --custom "status=='Cancelled'" --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --synchronization-id 00000000-0000-0000-0000-000000000000
"""

helps['datashare consumer share-subscription list-source-share-synchronization-setting'] = """
    type: command
    short-summary: List synchronization settings set on a share
    examples:
      - name: List synchronization settings
        text: |-
               az datashare consumer share-subscription list-source-share-synchronization-setting --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSub
"""

helps['datashare consumer share-subscription synchronization list'] = """
    type: command
    short-summary: List synchronizations of a share subscription
    examples:
      - name: List synchronizations
        text: |-
               az datashare consumer share-subscription synchronization list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSub
"""

helps['datashare consumer share-subscription wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare share subscription is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare share subscription is successfully provisioned.
          text: az datashare consumer share-subscription wait --account-name MyAccount --resource-group MyResourceGroup --name MyShareSubscription --created
"""

helps['datashare consumer share-subscription list-source-dataset'] = """
    type: command
    short-summary: List source datasets of a share subscription
    examples:
      - name: List source datasets
        text: |-
               az datashare consumer share-subscription list-source-dataset --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShare
"""

helps['datashare synchronization-setting'] = """
    type: group
    short-summary: Commands for providers to manage datashare synchronization settings
"""

helps['datashare synchronization-setting list'] = """
    type: command
    short-summary: List synchronization settings in a share
    examples:
      - name: List synchronization settings
        text: |-
               az datashare synchronization-setting list --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare
"""

helps['datashare synchronization-setting show'] = """
    type: command
    short-summary: Show a synchronization setting in a share
    examples:
      - name: Show a synchronization setting
        text: |-
               az datashare synchronization-setting show --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare --name MySyncrhonizationSetting
"""

helps['datashare synchronization-setting create'] = """
    type: command
    short-summary: Create a synchronization setting
    examples:
      - name: Create a synchronization setting
        text: |-
               az datashare synchronization-setting create --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare --name MyDataset --recurrence-interval Day --synchronization-time "2020-04-05 10:50:00 +00:00" --kind ScheduleBased
"""

helps['datashare synchronization-setting delete'] = """
    type: command
    short-summary: Delete a synchronization setting in a share
    examples:
      - name: Delete a synchronization setting
        text: |-
               az datashare synchronization-setting delete --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare --name MySyncrhonizationSetting
"""

helps['datashare synchronization-setting wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare synchronization setting is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare synchronization setting is successfully provisioned.
          text: az datashare synchronization-setting wait --account-name MyAccount --resource-group MyResourceGroup --share-name MyShare --name MySyncrhonizationSetting --created
"""

helps['datashare consumer trigger'] = """
    type: group
    short-summary: Commands for consumers to manage datashare consumer triggers
"""

helps['datashare consumer trigger list'] = """
    type: command
    short-summary: List triggers in a share subscription
    examples:
      - name: List triggers
        text: |-
               az datashare consumer trigger list --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription
"""

helps['datashare consumer trigger show'] = """
    type: command
    short-summary: Show a trigger in a share subscription
    examples:
      - name: Show a trigger
        text: |-
               az datashare consumer trigger show --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --name MyTrigger
"""

helps['datashare consumer trigger create'] = """
    type: command
    short-summary: Create a trigger
    examples:
      - name: Create a trigger
        text: |-
               az datashare consumer trigger create --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --name MyTrigger --recurrence-interval Day --synchronization-time "2020-04-05 10:50:00 +00:00" --kind ScheduleBased
"""

helps['datashare consumer trigger delete'] = """
    type: command
    short-summary: Delete a trigger in a share subscription
    examples:
      - name: Delete a trigger
        text: |-
               az datashare consumer trigger delete --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --name MyTrigger
"""

helps['datashare consumer trigger wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the datashare trigger is met.
    examples:
        - name: Pause executing next line of CLI script until the datashare trigger is successfully provisioned.
          text: az datashare consumer trigger wait --account-name MyAccount --resource-group MyResourceGroup --share-subscription-name MyShareSubscription --name MyTrigger --created
"""
