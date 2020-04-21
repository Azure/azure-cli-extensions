# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
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
               az datashare account create --location "West US 2" --tags
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
               "SampleResourceGroup" --share-name "Share1" --kind "ScheduleBased"
               --synchronization-setting-name "Dataset1"
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
