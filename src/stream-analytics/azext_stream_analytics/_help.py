# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['stream-analytics job'] = """
    type: group
    short-summary: Commands to manage stream-analytics streaming job.
"""

helps['stream-analytics job create'] = """
    type: command
    short-summary: Creates a streaming job or replaces an already existing streaming job.
    examples:
      - name: Create a streaming job
        text: |-
               az stream-analytics job create --resource-group MyResourceGroup --name MyJobName \\
               --location "West US" --output-error-policy "Drop" --events-outoforder-policy "Drop" \\
               --events-outoforder-max-delay 5 --events-late-arrival-max-delay 16 --data-locale "en-US"
"""

helps['stream-analytics job update'] = """
    type: command
    short-summary: Updates existing streaming job.
    examples:
      - name: Update a streaming job
        text: |-
               az stream-analytics job update --resource-group MyResourceGroup --name MyJobName \\
               --events-outoforder-max-delay 21 --events-late-arrival-max-delay 13
"""

helps['stream-analytics job delete'] = """
    type: command
    short-summary: Deletes a streaming job.
    examples:
      - name: Delete a streaming job
        text: |-
               az stream-analytics job delete --resource-group MyResourceGroup --name MyJobName
"""

helps['stream-analytics job show'] = """
    type: command
    short-summary: Gets details about the specified streaming job.
    examples:
      - name: Get a streaming job
        text: |-
               az stream-analytics job show --resource-group MyResourceGroup --name MyJobName
      - name: Get a streaming job and expand its inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job show --resource-group MyResourceGroup --name MyJobName --expand-all
"""

helps['stream-analytics job list'] = """
    type: command
    short-summary: Lists all of the streaming jobs in the specified resource group.
    examples:
      - name: List all streaming jobs in current subscription
        text: |-
               az stream-analytics job list
      - name: List all streaming jobs in a resource group
        text: |-
               az stream-analytics job list --resource-group MyResourceGroup
      - name: List all streaming jobs and expand their inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job list --resource-group MyResourceGroup --expand-all
"""

helps['stream-analytics job start'] = """
    type: command
    short-summary: Starts a streaming job.
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
    short-summary: Stops a running streaming job.
    examples:
      - name: Stop a streaming job
        text: |-
               az stream-analytics job stop --resource-group MyResourceGroup --name MyJobName
"""

helps['stream-analytics input'] = """
    type: group
    short-summary: Commands to manage stream-analytics input.
"""

helps['stream-analytics input create'] = """
    type: command
    short-summary: Creates an input or replaces an already existing input under an existing streaming job.
    examples:
      - name: Create an input
        text: |-
               az stream-analytics input create --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyInputName --type Stream --datasource @datasource.json --serialization @serialization.json
               ("datasource.json" contains the following content)
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
                        "timeFormat": "HH"
                    }
                }
               ("serialization.json" contains the following content)
                {
                    "type": "Csv",
                    "properties": {
                        "fieldDelimiter": ",",
                        "encoding": "UTF8"
                    }
                }
"""

helps['stream-analytics input delete'] = """
    type: command
    short-summary: Deletes an input from the streaming job.
    examples:
      - name: Delete an input
        text: |-
               az stream-analytics input delete --resource-group MyResourceGroup --job-name MyJobName --name MyInputName
"""

helps['stream-analytics input show'] = """
    type: command
    short-summary: Gets details about the specified input.
    examples:
      - name: Get details about specified input
        text: |-
               az stream-analytics input show --resource-group MyResourceGroup --job-name MyJobName --name MyInputName
"""

helps['stream-analytics input list'] = """
    type: command
    short-summary: Lists all of the inputs under the specified streaming job.
    examples:
      - name: List all inputs in a streaming job
        text: |-
               az stream-analytics input list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics input test'] = """
    type: command
    short-summary: Tests whether an input’s datasource is reachable and usable by the Azure Stream Analytics service.
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
    short-summary: Creates an output or replaces an already existing output under an existing streaming job.
    examples:
      - name: Create an output
        text: |-
               az stream-analytics output create --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName --datasource @datasource.json --serialization @serialization.json
               ("datasource.json" contains the following content)
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
               ("serialization.json" contains the following content)
                {
                    "type": "Json",
                    "properties": {
                        "encoding": "UTF8",
                        "format": "Array"
                    }
                }
"""

helps['stream-analytics output delete'] = """
    type: command
    short-summary: Deletes an output from the streaming job.
    examples:
      - name: Delete an output
        text: |-
               az stream-analytics output delete --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName
"""

helps['stream-analytics output show'] = """
    type: command
    short-summary: Gets details about the specified output.
    examples:
      - name: Get details about an output
        text: |-
               az stream-analytics output show --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyOutputName
"""

helps['stream-analytics output list'] = """
    type: command
    short-summary: Lists all of the outputs under the specified streaming job.
    examples:
      - name: List all outputs in a streaming job
        text: |-
               az stream-analytics output list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics output test'] = """
    type: command
    short-summary: Tests an output
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
    short-summary: Creates a transformation or replaces an already existing transformation under an existing streaming job.
    examples:
      - name: Create a transformation
        text: |-
               az stream-analytics transformation create --resource-group MyResourceGroup --job-name MyJobName \\
               --name Transformation --streaming-units "6" --transformation-query "Select Id, Name from inputtest"
"""

helps['stream-analytics transformation update'] = """
    type: command
    short-summary: Updates transformation under an existing streaming job.
    examples:
      - name: Update a transformation
        text: |-
               az stream-analytics transformation update --resource-group MyResourceGroup --job-name MyJobName \\
               --name Transformation --transformation-query "New query"
"""

helps['stream-analytics transformation show'] = """
    type: command
    short-summary: Gets details about the specified transformation.
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
    short-summary: Creates a function or replaces an already existing function under an existing streaming job.
    examples:
      - name: Create a function
        text: |-
               az stream-analytics function create --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyFunctionName --inputs @inputs.json --function-output @output.json --binding @binding.json
               ("inputs.json" contains the following content)
                [
                    {
                        "dataType": "Any"
                    }
                ]
               ("output.json" contains the following content)
                {
                    "dataType": "Any"
                }
               ("binding.json" contains the following content)
                {
                    "type": "Microsoft.StreamAnalytics/JavascriptUdf",
                    "properties": {
                        "script": "function (x, y) { return x + y; }"
                    }
                }
"""

helps['stream-analytics function delete'] = """
    type: command
    short-summary: Deletes a function from the streaming job.
    examples:
      - name: Delete a function
        text: |-
               az stream-analytics function delete --resource-group MyResourceGroup --job-name MyJobName \\
               --name MyFunctionName
"""

helps['stream-analytics function show'] = """
    type: command
    short-summary: Gets details about the specified function.
    examples:
      - name: Get details about a function
        text: |-
               az stream-analytics function show --resource-group MyResourceGroup --job-name MyJobName --name \\
               MyFunctionName
"""

helps['stream-analytics function list'] = """
    type: command
    short-summary: Lists all of the functions under the specified streaming job.
    examples:
      - name: List all functions in a streaming job
        text: |-
               az stream-analytics function list --resource-group MyResourceGroup --job-name MyJobName
"""

helps['stream-analytics function test'] = """
    type: command
    short-summary: Tests if the information provided for a function is valid.
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
    short-summary: Retrieves quota information in a particular region.
    examples:
      - name: List quota information in West US
        text: |-
               az stream-analytics quota show --location "West US"
"""
