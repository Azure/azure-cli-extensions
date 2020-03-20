# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import

helps['stream-analytics'] = """
    type: group
    short-summary: Manage Stream Analytics.
"""

helps['stream-analytics job'] = """
    type: group
    short-summary: Commands to manage stream-analytics streaming job.
"""

helps['stream-analytics job create'] = """
    type: command
    short-summary: Create a streaming job or replaces an already existing streaming job.
    examples:
      - name: Create a streaming job
        text: |-
               az stream-analytics job create --resource-group MyResourceGroup --name MyJobName \\
               --location "West US" --output-error-policy "Drop" --events-outoforder-policy "Drop" \\
               --events-outoforder-max-delay 5 --events-late-arrival-max-delay 16 --data-locale "en-US"
"""

helps['stream-analytics job update'] = """
    type: command
    short-summary: Update existing streaming job.
    examples:
      - name: Update a streaming job
        text: |-
               az stream-analytics job update --resource-group MyResourceGroup --name MyJobName \\
               --events-outoforder-max-delay 21 --events-late-arrival-max-delay 13
"""

helps['stream-analytics job delete'] = """
    type: command
    short-summary: Delete a streaming job.
    examples:
      - name: Delete a streaming job
        text: |-
               az stream-analytics job delete --resource-group MyResourceGroup --name MyJobName
"""

helps['stream-analytics job show'] = """
    type: command
    short-summary: Get details about the specified streaming job.
    examples:
      - name: Get a streaming job
        text: |-
               az stream-analytics job show --resource-group MyResourceGroup --name MyJobName
      - name: Get a streaming job and expand its inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job show --resource-group MyResourceGroup --name MyJobName --expand
"""

helps['stream-analytics job list'] = """
    type: command
    short-summary: List all of the streaming jobs in the specified resource group.
    examples:
      - name: List all streaming jobs in current subscription
        text: |-
               az stream-analytics job list
      - name: List all streaming jobs in a resource group
        text: |-
               az stream-analytics job list --resource-group MyResourceGroup
      - name: List all streaming jobs and expand their inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job list --resource-group MyResourceGroup --expand
"""

helps['stream-analytics job start'] = """
    type: command
    short-summary: Start a streaming job.
    examples:
      - name: Start a streaming job with LastOutputEventTime output start mode
        text: |-
               az stream-analytics job start --resource-group MyResourceGroup --name MyJobName --output-start-mode LastOutputEventTime
      - name: Start a streaming job with JobStartTime output start mode
        text: |-
               az stream-analytics job start --resource-group MyResourceGroup --name MyJobName --output-start-mode JobStartTime
      - name: Start a streaming job with CustomTime output start mode
        text: |-
               az stream-analytics job start --resource-group MyResourceGroup --name MyJobName --output-start-mode CustomTime --output-start-time 2020-01-01T00:00:00Z
"""

helps['stream-analytics job stop'] = """
    type: command
    short-summary: Stop a running streaming job.
    examples:
      - name: Stop a streaming job
        text: |-
               az stream-analytics job stop --resource-group MyResourceGroup --name MyJobName
"""

helps['stream-analytics job wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of the streaming job is met.
examples:
  - name: Pause executing next line of CLI script until the streaming job is successfully provisioned.
    text: |
        az stream-analytics job wait --resource-group MyResourceGroup --name MyJobName --created
"""

helps['stream-analytics input'] = """
    type: group
    short-summary: Commands to manage stream-analytics input.
"""

helps['stream-analytics input create'] = """
    type: command
    short-summary: Create an input or replaces an already existing input under an existing streaming job.
    examples:
      - name: Create an input
        text: |-
               az stream-analytics input create --resource-group MyResourceGroup --job-name MyJobName \\
               --name MyInputName --type Stream --datasource @datasource.json --serialization \\
               @serialization.json
                (below is an example of Blob Storage for "datasource.json")
                {
                    "type": "Microsoft.Storage/Blob",
                    "properties": {
                        "storageAccounts": [
                            {
                                "accountName": "someAccountName",
                                "accountKey": "someAccountKey=="
                            }
                        ],
                        "container": "state",
                        "pathPattern": "{date}/{time}",
                        "dateFormat": "yyyy/MM/dd",
                        "timeFormat": "HH",
                        "sourcePartitionCount": 16
                    }
                }
                (below is an example of Event Hub for "datasource.json")
                {
                    "type": "Microsoft.ServiceBus/EventHub",
                    "properties": {
                        "serviceBusNamespace": "sdktest",
                        "sharedAccessPolicyName": "RootManageSharedAccessKey",
                        "sharedAccessPolicyKey": "someSharedAccessPolicyKey==",
                        "eventHubName": "sdkeventhub",
                        "consumerGroupName": "sdkconsumergroup"
                    }
                }
                (below is an example of Iot Hub for "datasource.json")
                {
                    "type": "Microsoft.Devices/IotHubs",
                    "properties": {
                        "iotHubNamespace": "iothub",
                        "sharedAccessPolicyName": "owner",
                        "sharedAccessPolicyKey": "sharedAccessPolicyKey=",
                        "consumerGroupName": "sdkconsumergroup",
                        "endpoint": "messages/events"
                    }
                }
                (below is an example of Csv for "serialization.json")
                {
                    "type": "Csv",
                    "properties": {
                        "fieldDelimiter": ",",
                        "encoding": "UTF8"
                    }
                }
                (below is an example of Json for "serialization.json")
                {
                    "type": "Json",
                    "properties": {
                        "encoding": "UTF8"
                    }
                }
                (below is an example of Avro for "serialization.json")
                {
                    "type": "Avro"
                }
"""

helps['stream-analytics input delete'] = """
    type: command
    short-summary: Delete an input from the streaming job.
    examples:
      - name: Delete an input
        text: |-
               az stream-analytics input delete --resource-group MyResourceGroup --job-name MyJobName --name MyInputName
"""

helps['stream-analytics input show'] = """
    type: command
    short-summary: Get details about the specified input.
    examples:
      - name: Get details about specified input
        text: |-
               az stream-analytics input show --resource-group MyResourceGroup --job-name MyJobName --name MyInputName
"""

helps['stream-analytics input list'] = """
    type: command
    short-summary: List all of the inputs under the specified streaming job.
    examples:
      - name: List all inputs in a streaming job
        text: |-
               az stream-analytics input list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics input test'] = """
    type: command
    short-summary: Test an input.
    examples:
      - name: Test the connection for an input
        text: |-
               az stream-analytics input test --resource-group MyResourceGroup --job-name MyJobName --name MyInputName
"""

helps['stream-analytics output'] = """
    type: group
    short-summary: Commands to manage stream-analytics output.
"""

helps['stream-analytics output create'] = """
    type: command
    short-summary: Create an output or replaces an already existing output under an existing streaming job.
    examples:
      - name: Create an output
        text: |-
               az stream-analytics output create --resource-group MyResourceGroup --job-name MyJobName \\
               --name MyOutputName --datasource @datasource.json --serialization @serialization.json
                (below is an example of DataLake for "datasource.json")
                {
                    "type": "Microsoft.DataLake/Accounts",
                    "properties": {
                        "accountName": "someaccount",
                        "tenantId": "cea4e98b-c798-49e7-8c40-4a2b3beb47dd",
                        "refreshToken": "someRefreshToken==",
                        "tokenUserPrincipalName": "bobsmith@contoso.com",
                        "tokenUserDisplayName": "Bob Smith",
                        "filePathPrefix": "{date}/{time}",
                        "dateFormat": "yyyy/MM/dd",
                        "timeFormat": "HH"
                    }
                }
                (below is an example of SQL Database for "datasource.json")
                {
                    "type": "Microsoft.Sql/Server/Database",
                    "properties": {
                        "server": "someServer",
                        "database": "someDatabase",
                        "user": "someUser",
                        "password": "somePassword",
                        "table": "someTable"
                    }
                }
                (below is an example of Table Storage for "datasource.json")
                {
                    "type": "Microsoft.Storage/Table",
                    "properties": {
                        "accountName": "someAccountName",
                        "accountKey": "accountKey==",
                        "table": "samples",
                        "partitionKey": "partitionKey",
                        "rowKey": "rowKey",
                        "columnsToRemove": [
                            "column1",
                            "column2"
                        ],
                        "batchSize": 25
                    }
                }
                (below is an example of Blob Storage for "datasource.json")
                {
                    "type": "Microsoft.Storage/Blob",
                    "properties": {
                        "storageAccounts": [
                            {
                                "accountName": "someAccountName",
                                "accountKey": "accountKey=="
                            }
                        ],
                        "container": "state",
                        "pathPattern": "{date}/{time}",
                        "dateFormat": "yyyy/MM/dd",
                        "timeFormat": "HH"
                    }
                }
                (below is an example of DocumentDB for "datasource.json")
                {
                    "type": "Microsoft.Storage/DocumentDB",
                    "properties": {
                        "accountId": "someAccountId",
                        "accountKey": "accountKey==",
                        "database": "db01",
                        "collectionNamePattern": "collection",
                        "partitionKey": "key",
                        "documentId": "documentId"
                    }
                }
                (below is an example of Event Hub for "datasource.json")
                {
                    "type": "Microsoft.ServiceBus/EventHub",
                    "properties": {
                        "serviceBusNamespace": "sdktest",
                        "sharedAccessPolicyName": "RootManageSharedAccessKey",
                        "sharedAccessPolicyKey": "sharedAccessPolicyKey=",
                        "eventHubName": "sdkeventhub",
                        "partitionKey": "partitionKey"
                    }
                }
                (below is an example of PowerBI for "datasource.json")
                {
                    "type": "PowerBI",
                    "properties": {
                        "dataset": "someDataset",
                        "table": "someTable",
                        "refreshToken": "someRefreshToken==",
                        "tokenUserPrincipalName": "bobsmith@contoso.com",
                        "tokenUserDisplayName": "Bob Smith",
                        "groupId": "ac40305e-3e8d-43ac-8161-c33799f43e95",
                        "groupName": "MyPowerBIGroup"
                    }
                }
                (below is an example of Service Bus Queue for "datasource.json")
                {
                    "type": "Microsoft.ServiceBus/Queue",
                    "properties": {
                        "serviceBusNamespace": "sdktest",
                        "sharedAccessPolicyName": "RootManageSharedAccessKey",
                        "sharedAccessPolicyKey": "sharedAccessPolicyKey=",
                        "queueName": "sdkqueue",
                        "propertyColumns": [
                            "column1",
                            "column2"
                        ]
                    }
                }
                (below is an example of Service Bus Topic for "datasource.json")
                {
                    "type": "Microsoft.ServiceBus/Topic",
                    "properties": {
                        "serviceBusNamespace": "sdktest",
                        "sharedAccessPolicyName": "RootManageSharedAccessKey",
                        "sharedAccessPolicyKey": "sharedAccessPolicyKey=",
                        "topicName": "sdktopic",
                        "propertyColumns": [
                            "column1",
                            "column2"
                        ]
                    }
                }
                (below is an example of Csv for "serialization.json")
                {
                    "type": "Csv",
                    "properties": {
                        "fieldDelimiter": ",",
                        "encoding": "UTF8"
                    }
                }
                (below is an example of Json for "serialization.json")
                {
                    "type": "Json",
                    "properties": {
                        "encoding": "UTF8",
                        "format": "Array"
                    }
                }
                (below is an example of Avro for "serialization.json")
                {
                    "type": "Avro"
                }
"""

helps['stream-analytics output delete'] = """
    type: command
    short-summary: Delete an output from the streaming job.
    examples:
      - name: Delete an output
        text: |-
               az stream-analytics output delete --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName
"""

helps['stream-analytics output show'] = """
    type: command
    short-summary: Get details about the specified output.
    examples:
      - name: Get details about an output
        text: |-
               az stream-analytics output show --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName
"""

helps['stream-analytics output list'] = """
    type: command
    short-summary: List all of the outputs under the specified streaming job.
    examples:
      - name: List all outputs in a streaming job
        text: |-
               az stream-analytics output list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics output test'] = """
    type: command
    short-summary: Test an output
    examples:
      - name: Test the connection for an output
        text: |-
               az stream-analytics output test --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName
"""

helps['stream-analytics transformation'] = """
    type: group
    short-summary: Commands to manage stream-analytics transformation.
"""

helps['stream-analytics transformation create'] = """
    type: command
    short-summary: Create a transformation or replaces an already existing transformation under an existing streaming job.
    examples:
      - name: Create a transformation
        text: |-
               az stream-analytics transformation create --resource-group MyResourceGroup --job-name MyJobName \\
               --name Transformation --streaming-units "6" --transformation-query "Select Id, Name from inputtest"
"""

helps['stream-analytics transformation update'] = """
    type: command
    short-summary: Update transformation under an existing streaming job.
    examples:
      - name: Update a transformation
        text: |-
               az stream-analytics transformation update --resource-group MyResourceGroup --job-name MyJobName \\
               --name Transformation --transformation-query "New query"
"""

helps['stream-analytics transformation show'] = """
    type: command
    short-summary: Get details about the specified transformation.
    examples:
      - name: Get a transformation
        text: |-
               az stream-analytics transformation show --resource-group MyResourceGroup --job-name MyJobName \\
               --name Transformation
"""

helps['stream-analytics function'] = """
    type: group
    short-summary: Commands to manage stream-analytics function.
"""

helps['stream-analytics function create'] = """
    type: command
    short-summary: Create a function or replaces an already existing function under an existing streaming job.
    examples:
      - name: Create a function
        text: |-
               az stream-analytics function create --resource-group MyResourceGroup --job-name MyJobName \\
               --name MyFunctionName --inputs @inputs.json --function-output @output.json --binding \\
               @binding.json
                (below is an example for "inputs.json")
                [
                    {
                        "dataType": "Any"
                    }
                ]
                (below is an example for "output.json")
                {
                    "dataType": "Any"
                }
                (below is an example of JavascripUDF for "binding.json")
                {
                    "type": "Microsoft.StreamAnalytics/JavascriptUdf",
                    "properties": {
                        "script": "function (x, y) { return x + y; }"
                    }
                }
                (below is an example of Azure Machine Learning for "binding.json")
                {
                    "type": "Microsoft.MachineLearning/WebService",
                    "properties": {
                        "endpoint": "someAzureMLEndpointURL",
                        "apiKey": "someApiKey==",
                        "inputs": {
                            "name": "input1",
                            "columnNames": [
                                {
                                    "name": "tweet",
                                    "dataType": "string",
                                    "mapTo": 0
                                }
                            ]
                        },
                        "outputs": [
                            {
                                "name": "Sentiment",
                                "dataType": "string"
                            }
                        ],
                        "batchSize": 1000
                    }
                }
"""

helps['stream-analytics function delete'] = """
    type: command
    short-summary: Delete a function from the streaming job.
    examples:
      - name: Delete a function
        text: |-
               az stream-analytics function delete --resource-group MyResourceGroup --job-name MyJobName \\
               --name MyFunctionName
"""

helps['stream-analytics function show'] = """
    type: command
    short-summary: Get details about the specified function.
    examples:
      - name: Get details about a function
        text: |-
               az stream-analytics function show --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyFunctionName
"""

helps['stream-analytics function list'] = """
    type: command
    short-summary: List all of the functions under the specified streaming job.
    examples:
      - name: List all functions in a streaming job
        text: |-
               az stream-analytics function list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics function test'] = """
    type: command
    short-summary: Test if the information provided for a function is valid.
    examples:
      - name: Test the connection for a function
        text: |-
               az stream-analytics function test --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyFunctionName
"""

helps['stream-analytics quota'] = """
    type: group
    short-summary: Commands to show quota information.
"""

helps['stream-analytics quota show'] = """
    type: command
    short-summary: Retrieve quota information in a particular region.
    examples:
      - name: List quota information in West US
        text: |-
               az stream-analytics quota show --location "West US"
"""
