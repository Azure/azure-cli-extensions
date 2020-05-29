# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['timeseriesinsights'] = """
type: group
short-summary: Manage Azure Time Series Insights.
"""

helps['timeseriesinsights environment'] = """
type: group
short-summary: Commands to manage timeseriesinsights environment.
"""

helps['timeseriesinsights environment standard'] = """
type: group
short-summary: Create or update a standard environment in the specified subscription and resource group.
"""

helps['timeseriesinsights environment standard create'] = """
type: command
short-summary: Create or update a standard environment in the specified subscription and resource group.
examples:
  - name: Create a standard environment
    text: az timeseriesinsights environment standard create -g {rg} -n {env} --location westus --sku-name S1 --sku-capacity 1 --data-retention-time 31 --partition-key DeviceId1 --storage-limit-exceeded-behavior PauseIngress
"""

helps['timeseriesinsights environment standard update'] = """
type: command
short-summary: Update a standard environment in the specified subscription and resource group.
examples:
  - name: Update sku capacity
    text: az timeseriesinsights environment standard update -g {rg} -n {env} --sku-name S1 --sku-capacity 2
  - name: Update data retention days
    text: az timeseriesinsights environment standard update -g {rg} -n {env} --data-retention-time 8
  - name: Update storage limit exceeded behavior
    text: az timeseriesinsights environment standard update -g {rg} -n {env} --storage-limit-exceeded-behavior PurgeOldData
"""

helps['timeseriesinsights environment longterm'] = """
type: group
short-summary: Create or update a longterm environment in the specified subscription and resource group.
"""

helps['timeseriesinsights environment longterm create'] = """
type: command
short-summary: Create or update a longterm environment in the specified subscription and resource group.
examples:
  - name: Create storage account and use it to create a longterm environment
    text: |
        storage=mystorageaccount
        rg={rg}
        az storage account create -g $rg -n $storage --https-only
        key=$(az storage account keys list -g $rg -n $storage --query [0].value --output tsv)
        az timeseriesinsights environment longterm create -g $rg -n {env} --location westus --sku-name L1 --sku-capacity 1 --data-retention 7 --time-series-id-properties DeviceId1 --storage-account-name $storage --storage-management-key $key
"""

helps['timeseriesinsights environment longterm update'] = """
type: command
short-summary: Update a longterm environment in the specified subscription and resource group.
examples:
  - name: Update dataRetention
    text: az timeseriesinsights environment longterm update -g {rg} -n {env} --data-retention 8
  - name: Update storageManagementKey
    text: az timeseriesinsights environment longterm update -g {rg} -n {env} --storage-management-key xxx
"""

helps['timeseriesinsights environment delete'] = """
type: command
short-summary: Delete the environment with the specified name in the specified subscription and resource group.
examples:
  - name: Delete an environments
    text: |-
           az timeseriesinsights environment delete -g {rg} -n {env}
"""

helps['timeseriesinsights environment show'] = """
type: command
short-summary: Show the environment with the specified name in the specified subscription and resource group.
examples:
  - name: Show an environments
    text: |-
           az timeseriesinsights environment show -g {rg} -n {env}
"""

helps['timeseriesinsights environment list'] = """
type: command
short-summary: List all the available environments associated with the subscription and within the specified resource group.
examples:
  - name: List environments by resource group
    text: |-
           az timeseriesinsights environment list -g {rg}
  - name: List environments by subscription
    text: |-
           az timeseriesinsights environment list
"""

helps['timeseriesinsights event-source'] = """
type: group
short-summary: Commands to manage timeseriesinsights event source.
"""

helps['timeseriesinsights event-source eventhub'] = """
type: group
short-summary: Create or update an event hub event source under the specified environment.
"""

helps['timeseriesinsights event-source eventhub create'] = """
type: command
short-summary: Create or update an event hub event source under the specified environment.
examples:
  - name: Create an eventhub and use it for event source
    text: |
        rg={rg}
        ehns={eventhub_namespace}
        eh={eventhub_name}
        az eventhubs namespace create -g $rg -n $ehns
        es_resource_id=$(az eventhubs eventhub create -g $rg -n $eh --namespace-name $ehns --query id --output tsv)
        shared_access_key=$(az eventhubs namespace authorization-rule keys list -g $rg --namespace-name $ehns -n RootManageSharedAccessKey --query primaryKey --output tsv)
        az timeseriesinsights event-source eventhub create -g $rg --environment-name {env} -n es1 --key-name RootManageSharedAccessKey --shared-access-key $shared_access_key --event-source-resource-id $es_resource_id --consumer-group-name '$Default' --timestamp-property-name DeviceId
"""

helps['timeseriesinsights event-source eventhub update'] = """
type: command
short-summary: Create or update an event source under the specified environment.
examples:
  - name: Update timestampPropertyName
    text: az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} -n {es} --timestamp-property-name DeviceId1
  - name: Update localTimestamp (Currently only Embedded is supported)
    text: az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} -n {es} --local-timestamp-format Embedded
  - name: Update sharedAccessKey
    text: az timeseriesinsights event-source eventhub update -g {rg} --environment-name {env} -n {es} --shared-access-key {shared_access_key}
"""

helps['timeseriesinsights event-source iothub'] = """
type: group
short-summary: Create or update an iothub event source under the specified environment.
"""

helps['timeseriesinsights event-source iothub create'] = """
type: command
short-summary: Create or update an iothub event source under the specified environment.
examples:
  - name: Create an iothub and use it for event source
    text: |
        rg={rg}
        iothub={iothub_name}
        es_resource_id=$(az iot hub create -g $rg -n $iothub --query id --output tsv)
        shared_access_key=$(az iot hub policy list -g $rg --hub-name $iothub --query "[?keyName=='iothubowner'].primaryKey" --output tsv)
        az timeseriesinsights event-source iothub create -g $rg --environment-name {env} -n es2 --consumer-group-name '$Default' --key-name iothubowner --shared-access-key $shared_access_key --event-source-resource-id $es_resource_id --timestamp-property-name DeviceId
"""

helps['timeseriesinsights event-source iothub update'] = """
type: command
short-summary: Create or update an event source under the specified environment.
examples:
  - name: Update timestampPropertyName
    text: az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} -n {es} --timestamp-property-name DeviceId1
  - name: Update localTimestamp (Currently only Embedded is supported)
    text: az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} -n {es} --local-timestamp-format Embedded
  - name: Update sharedAccessKey
    text: az timeseriesinsights event-source iothub update -g {rg} --environment-name {env} -n {es} --shared-access-key {shared_access_key}
"""

helps['timeseriesinsights event-source delete'] = """
type: command
short-summary: Delete the event source with the specified name in the specified subscription, resource group, and environment
examples:
  - name: Delete event-source
    text: az timeseriesinsights event-source delete -g {rg} --environment-name {env} -n es1
"""

helps['timeseriesinsights event-source show'] = """
type: command
short-summary: Show the event source with the specified name in the specified environment.
examples:
  - name: Show event-source
    text: az timeseriesinsights event-source show -g {rg} --environment-name {env} -n es1
"""

helps['timeseriesinsights event-source list'] = """
type: command
short-summary: List all the available event sources associated with the subscription and within the specified resource group and environment.
examples:
  - name: List event-source by environment
    text: az timeseriesinsights event-source list -g {rg} --environment-name {env}
"""

helps['timeseriesinsights reference-data-set'] = """
type: group
short-summary: Commands to manage timeseriesinsights reference data set.
"""

helps['timeseriesinsights reference-data-set create'] = """
type: command
short-summary: Create or update a reference data set in the specified environment.
examples:
  - name: Create reference-data-set
    text: az timeseriesinsights reference-data-set create -g {rg} --environment-name {env} -n {rds} --key-properties DeviceId1 String DeviceFloor Double --data-string-comparison-behavior Ordinal
"""

helps['timeseriesinsights reference-data-set update'] = """
type: command
short-summary: Create or update a reference data set in the specified environment.
examples:
  - name: Update reference-data-set
    text: az timeseriesinsights reference-data-set update -g {rg} --environment-name {env} -n {rds} --tags mykey=myvalue
"""

helps['timeseriesinsights reference-data-set delete'] = """
type: command
short-summary: Delete the reference data set with the specified name in the specified subscription, resource group, and environment
examples:
  - name: Delete reference-data-set
    text: |-
           az timeseriesinsights reference-data-set delete -g {rg} --environment-name {env} -n {rds}
"""

helps['timeseriesinsights reference-data-set show'] = """
type: command
short-summary: Show the reference data set with the specified name in the specified environment.
examples:
  - name: Show reference-data-set
    text: |-
           az timeseriesinsights reference-data-set show -g {rg} --environment-name {env} -n {rds}
"""

helps['timeseriesinsights reference-data-set list'] = """
type: command
short-summary: List all the available reference data sets associated with the subscription and within the specified resource group and environment.
examples:
  - name: List reference-data-set by environment
    text: |-
           az timeseriesinsights reference-data-set list -g {rg} --environment-name {env}
"""

helps['timeseriesinsights access-policy'] = """
type: group
short-summary: Commands to manage timeseriesinsights access policy.
"""

helps['timeseriesinsights access-policy create'] = """
type: command
short-summary: Create or update an access policy in the specified environment.
examples:
  - name: Create access-policy
    text: az timeseriesinsights access-policy create -g {rg} --environment-name {env} -n ap1 --principal-object-id 001 --description "some description" --roles Contributor Reader
"""

helps['timeseriesinsights access-policy update'] = """
type: command
short-summary: Create or update an access policy in the specified environment.
examples:
  - name: Update access-policy
    text: |-
           az timeseriesinsights access-policy update -g {rg} --environment-name \\
           {env} -n {ap} --roles "Reader,Contributor"
"""

helps['timeseriesinsights access-policy delete'] = """
type: command
short-summary: Delete the access policy with the specified name in the specified subscription, resource group, and environment
examples:
  - name: Delete access-policy
    text: |-
           az timeseriesinsights access-policy delete -g {rg} --environment-name {env} -n {ap}
"""

helps['timeseriesinsights access-policy show'] = """
type: command
short-summary: Show the access policy with the specified name in the specified environment.
examples:
  - name: Get access-policy
    text: |-
           az timeseriesinsights access-policy show -g {rg} --environment-name {env} -n {ap}
"""

helps['timeseriesinsights access-policy list'] = """
type: command
short-summary: List all the available access policies associated with the environment.
examples:
  - name: List access-policy by environment
    text: |-
           az timeseriesinsights access-policy list -g {rg} --environment-name {env}
"""
