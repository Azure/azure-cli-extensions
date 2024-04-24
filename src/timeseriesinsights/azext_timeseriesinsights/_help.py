# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['tsi environment list'] = """
    type: command
    short-summary: "List all the available environments associated with the subscription and within the specified resource group."
    examples:
      - name: EnvironmentsByResourceGroup
        text: |-
               az tsi environment list --resource-group "rg1"
      - name: EnvironmentsBySubscription
        text: |-
               az tsi environment list
"""

helps['tsi environment gen1'] = """
    type: group
    short-summary: "Manage a gen1 environment in the specified subscription and resource group."
"""

helps['tsi environment gen1 create'] = """
    type: command
    short-summary: "Create a gen1 environment in the specified subscription and resource group."
    parameters:
      - name: --sku
        short-summary: "The sku determines the type of environment, either S1 or S2. For Gen1 \
environments the sku determines the capacity of the environment, the ingress rate, and the billing rate."
        long-summary: |
            Usage: --sku name=XX capacity=XX

            name: Required. The name of this SKU.
            capacity: Required. The capacity of the sku. This value can be changed to support scale out of \
            environments after they have been created.
      - name: --key-properties --partition-key-properties
        short-summary: "The list of event properties which will be used to partition data in the environment. \
Currently, only a single partition key property is supported."
        long-summary: |
            Usage: --partition-key-properties name=XX type=XX

            name: The name of the property.
            type: The type of the property.

            Multiple actions can be specified by using more than one --partition-key-properties argument.
    examples:
      - name: EnvironmentsGen1Create
        text: |-
               az tsi environment gen1 create --name "env1" --location westus --data-retention-time \
"P31D" --partition-key-properties name="DeviceId1" type="String" --sku name="S1" capacity=1 --resource-group "rg1"
"""

helps['tsi environment gen1 update'] = """
    type: command
    short-summary: "Update a gen1 environment in the specified subscription and resource group."
    parameters:
      - name: --sku
        short-summary: "The sku determines the type of environment, either S1 or S2. For Gen1 \
environments the sku determines the capacity of the environment, the ingress rate, and the billing rate."
        long-summary: |
            Usage: --sku name=XX capacity=XX

            name: Required. The name of this SKU.
            capacity: Required. The capacity of the sku. This value can be changed to support scale out of \
            environments after they have been created.
    examples:
      - name: EnvironmentsGen1Update
        text: |-
               az tsi environment gen1 update --name "env1" --sku name="S1" capacity=2 \
               --resource-group "rg1" --data-retention-time "P30D" --storage-limit-exceeded-behavior PurgeOldData
"""

helps['tsi environment gen2'] = """
    type: group
    short-summary: Manage a gen2 environment in the specified subscription and resource group.
"""

helps['tsi environment gen2 create'] = """
    type: command
    short-summary: "Create a gen2 environment in the specified subscription and resource group."
    parameters:
      - name: --sku
        short-summary: "The sku determines the type of environment, L1."
        long-summary: |
            Usage: --sku name=XX capacity=XX

            name: Required. The name of this SKU.
            capacity: Required. The capacity of the sku.
      - name: --id-properties --time-series-id-properties
        short-summary: "The list of event properties which will be used to define the environment's time series id."
        long-summary: |
            Usage: --time-series-id-properties name=XX type=String

            name: The name of the property.
            type: The type of the property.

            Multiple actions can be specified by using more than one --time-series-id-properties argument.
      - name: --storage-config --storage-configuration
        short-summary: "The storage configuration provides the connection details that allows the Time Series Insights \
service to connect to the customer storage account that is used to store the environment's data."
        long-summary: |
            Usage: --storage-configuration account-name=XX management-key=XX

            account-name: Required. The name of the storage account that will hold the environment's Gen2 data.
            management-key: Required. The value of the management key that grants the Time Series Insights service \
write access to the storage account. This property is not shown in environment responses.
      - name: --warm-store-config --warm-store-configuration
        short-summary: "The warm store configuration provides the details to create a warm store cache that will \
retain a copy of the environment's data available for faster query."
        long-summary: |
            Usage: --warm-store-configuration data-retention=XX

            data-retention: Required. ISO8601 timespan specifying the number of days the environment's events will be \
available for query from the warm store.
    examples:
      - name: EnvironmentsGen2Create
        text: |-
               az tsi environment gen2 create --name "env2" --location westus --resource-group "rg1" \
               --sku name="L1" capacity=1 --time-series-id-properties name=idName type=String \
               --storage-configuration account-name=your-account-name management-key=your-account-key
"""

helps['tsi environment gen2 update'] = """
    type: command
    short-summary: "Update a gen2 environment in the specified subscription and resource group."
    parameters:
      - name: --storage-config --storage-configuration
        short-summary: "The storage configuration provides the connection details that allows the Time Series Insights \
service to connect to the customer storage account that is used to store the environment's data."
        long-summary: |
            Usage: --storage-configuration account-name=XX management-key=XX

            account-name: Required. The name of the storage account that will hold the environment's Gen2 data.
            management-key: Required. The value of the management key that grants the Time Series Insights service \
write access to the storage account. This property is not shown in environment responses.
      - name: --warm-store-config --warm-store-configuration
        short-summary: "The warm store configuration provides the details to create a warm store cache that will \
retain a copy of the environment's data available for faster query."
        long-summary: |
            Usage: --warm-store-configuration data-retention=XX

            data-retention: Required. ISO8601 timespan specifying the number of days the environment's events will be \
available for query from the warm store.
    examples:
      - name: EnvironmentsGen2Update
        text: |-
               az tsi environment gen2 update --name "env2" --resource-group "rg1" \
               --warm-store-configuration data-retention=P30D \
               --storage-configuration account-name=your-account-name management-key=your-account-key
"""

helps['tsi event-source'] = """
    type: group
    short-summary: Manage event source with timeseriesinsights
"""

helps['tsi event-source list'] = """
    type: command
    short-summary: "List all the available event sources associated with the subscription and within the specified \
resource group and environment."
    examples:
      - name: ListEventSourcesByEnvironment
        text: |-
               az tsi event-source list --environment-name "env1" --resource-group "rg1"
"""

helps['tsi event-source show'] = """
    type: command
    short-summary: "Show the event source with the specified name in the specified environment."
    examples:
      - name: GetEventHubEventSource
        text: |-
               az tsi event-source show --environment-name "env1" --name "es1" --resource-group "rg1"
"""

helps['tsi event-source eventhub'] = """
    type: group
    short-summary: Manage event source with timeseriesinsights sub group event-hub
"""

helps['tsi event-source eventhub create'] = """
    type: command
    short-summary: "Create an event source under the specified environment."
    examples:
      - name: CreateEventHubEventSource
        text: |-
               az tsi event-source eventhub create --environment-name "env1" --name "es1" \
--location westus --consumer-group-name "cgn" --event-hub-name "ehn" --event-source-resource-id "somePathInArm" \
--key-name "managementKey" --service-bus-namespace "sbn" --shared-access-key "someSecretvalue" \
--timestamp-property-name "someTimestampProperty" --resource-group "rg1"
"""

helps['tsi event-source eventhub update'] = """
    type: command
    short-summary: "Update an event source under the specified environment."
    examples:
      - name: UpdateEventHubEventSource
        text: |-
               az tsi event-source eventhub update --environment-name "env1" --name "es1" \
--shared-access-key "someSecretvalue" --timestamp-property-name "someTimestampProperty" --resource-group "rg1"
"""

helps['tsi event-source iothub'] = """
    type: group
    short-summary: Manage event source with timeseriesinsights sub group iot-hub
"""

helps['tsi event-source iothub create'] = """
    type: command
    short-summary: "Create an event source under the specified environment."
    examples:
      - name: CreateIotHubEventSource
        text: |-
               az tsi event-source iothub create -g "rg" --environment-name "env1" --name "eventsource" \
--consumer-group-name "consumer-group" --iot-hub-name "iothub" --location westus \
--key-name "key-name" --shared-access-key "someSecretvalue" --event-source-resource-id "resource-id"
"""

helps['tsi event-source iothub update'] = """
    type: command
    short-summary: "Update an event source under the specified environment."
    examples:
      - name: UpdateIotHubEventSource
        text: |-
               az tsi event-source iothub update -g "rg" --environment-name "env1" --name "eventsource" \
 --timestamp-property-name timestampProp --shared-access-key "someSecretvalue" --tags test=tag
"""

helps['tsi event-source delete'] = """
    type: command
    short-summary: "Delete the event source with the specified name in the specified subscription, resource group, \
and environment."
    examples:
      - name: DeleteEventSource
        text: |-
               az tsi event-source delete --environment-name "env1" --name "es1" --resource-group "rg1"
"""

helps['tsi reference-data-set list'] = """
    type: command
    short-summary: "List all the available reference data sets associated with the subscription and within the \
specified resource group and environment."
    examples:
      - name: ReferenceDataSetsListByEnvironment
        text: |-
               az tsi reference-data-set list --environment-name "env1" --resource-group "rg1"
"""

helps['tsi reference-data-set create'] = """
    type: command
    short-summary: "Create a reference data set in the specified environment."
    parameters:
      - name: --key-properties
        short-summary: "The list of key properties for the reference data set."
        long-summary: |
            Usage: --key-properties name=XX type=XX

            name: The name of the key property.
            type: The type of the key property.

            Multiple actions can be specified by using more than one --key-properties argument.
    examples:
      - name: ReferenceDataSetsCreate
        text: |-
               az tsi reference-data-set create --environment-name "env1" --location westus \
--key-properties name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" \
--resource-group "rg1"
"""
