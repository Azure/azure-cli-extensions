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
               az stream-analytics job create --resource-group "sjrg6936" --name "sj59" \\
               --location "West US" --events-out-of-order-policy "Drop" \\
               --output-error-policy "Drop" --events-out-of-order-max-delay-in-seconds "5" \\
               --events-late-arrival-max-delay-in-seconds "16" --data-locale "en-US"
"""

helps['stream-analytics job update'] = """
    type: command
    short-summary: Updates existing streaming job.
    examples:
      - name: Update a streaming job
        text: |-
               az stream-analytics job update --resource-group "sjrg6936" --name "sj59" \\
               --events-out-of-order-max-delay-in-seconds "21" \\
               --events-late-arrival-max-delay-in-seconds "13"
"""

helps['stream-analytics job delete'] = """
    type: command
    short-summary: Deletes a streaming job.
    examples:
      - name: Delete a streaming job
        text: |-
               az stream-analytics job delete --resource-group "sjrg6936" --name "sj59"
"""

helps['stream-analytics job show'] = """
    type: command
    short-summary: Gets details about the specified streaming job.
    examples:
      - name: Get a streaming job
        text: |-
               az stream-analytics streaming-job show --resource-group "sjrg6936" --name "sj59"
      - name: Get a streaming job and expand its inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics streaming-job show --resource-group "sjrg3276" --name "sj7804" --expand
"""

helps['stream-analytics job list'] = """
    type: command
    short-summary: Lists all of the streaming jobs in the specified resource group.
    examples:
      - name: List all streaming jobs
        text: |-
               az stream-analytics job list --resource-group "sjrg3276"
      - name: List all streaming jobs and expand their inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job list --resource-group "sjrg6936" --expand
"""

helps['stream-analytics job start'] = """
    type: command
    short-summary: Starts a streaming job.
    examples:
      - name: Start a streaming job with LastOutputEventTime output start mode
        text: |-
               az stream-analytics job start --resource-group "sjrg6936" --name "sj59" --output-start-mode LastOutputEventTime
      - name: Start a streaming job with JobStartTime output start mode
        text: |-
               az stream-analytics job start --resource-group "sjrg6936" --name "sj59" --output-start-mode JobStartTime
      - name: Start a streaming job with CustomTime output start mode
        text: |-
               az stream-analytics streaming-job start --resource-group "sjrg6936" --name "sj59" --output-start-mode CustomTime --output-start-time 2020-01-01T00:00:00Z
"""

helps['stream-analytics job stop'] = """
    type: command
    short-summary: Stops a running streaming job.
    examples:
      - name: Stop a streaming job
        text: |-
               az stream-analytics job stop --resource-group "sjrg6936" --name "sj59"
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
               az stream-analytics input create --resource-group "sjrg8440" --job-name "sj9597" --name \\
               "input7225" --datasource @datasource.json --serialization @serialization.json
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
               az stream-analytics input delete --resource-group "sjrg8440" --job-name "sj9597" --name \\
               "input7225"
"""

helps['stream-analytics input show'] = """
    type: command
    short-summary: Gets details about the specified input.
    examples:
      - name: Get details about specified input
        text: |-
               az stream-analytics input show --resource-group "sjrg8161" --job-name "sj6695" --name \\
               "input8899"
"""

helps['stream-analytics input list'] = """
    type: command
    short-summary: Lists all of the inputs under the specified streaming job.
    examples:
      - name: List all inputs in a streaming job
        text: |-
               az stream-analytics input list --resource-group "sjrg3276" --job-name "sj7804"
"""

helps['stream-analytics input test'] = """
    type: command
    short-summary: Tests whether an input’s datasource is reachable and usable by the Azure Stream Analytics service.
    examples:
      - name: Test the connection for an input
        text: |-
               az stream-analytics input test --resource-group "sjrg8440" --job-name "sj9597" --name \\
               "input7225"
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
               az stream-analytics output create --resource-group "sjrg5176" --job-name "sj2790" --name \\
               "output958" --datasource @datasource.json --serialization @serialization.json
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
               az stream-analytics output delete --resource-group "sjrg2157" --job-name "sj6458" --name \\
               "output1755"
"""

helps['stream-analytics output show'] = """
    type: command
    short-summary: Gets details about the specified output.
    examples:
      - name: Get details about an output
        text: |-
               az stream-analytics output show --resource-group "sjrg3410" --job-name "sj5095" --name \\
               "output3456"
"""

helps['stream-analytics output list'] = """
    type: command
    short-summary: Lists all of the outputs under the specified streaming job.
    examples:
      - name: List all outputs in a streaming job
        text: |-
               az stream-analytics output list --resource-group "sjrg2157" --job-name "sj6458"
"""

helps['stream-analytics output test'] = """
    type: command
    short-summary: Tests whether an output’s datasource is reachable and usable by the Azure Stream Analytics service.
    examples:
      - name: Test the connection for an output
        text: |-
               az stream-analytics output test --resource-group "sjrg2157" --job-name "sj6458" --name \\
               "output1755"
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
               az stream-analytics transformation create --resource-group "sjrg4423" --job-name "sj8374" \\
               --name "transformation952" --streaming-units "6" --query-string "Select Id, Name from inputtest"
"""

helps['stream-analytics transformation update'] = """
    type: command
    short-summary: Updates transformation under an existing streaming job.
    examples:
      - name: Update a transformation
        text: |-
               az stream-analytics transformation update --resource-group "sjrg4423" --job-name "sj8374" \\
               --name "transformation952" --query-string "New query"
"""

helps['stream-analytics transformation show'] = """
    type: command
    short-summary: Gets details about the specified transformation.
    examples:
      - name: Get a transformation
        text: |-
               az stream-analytics transformation show --resource-group "sjrg4423" --job-name "sj8374" \\
               --name "transformation952"
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
               az stream-analytics function create --resource-group "sjrg7" --job-name "sj9093" --name \\
               "function588" --function-inputs @inputs.json --function-output @output.json --function-binding \\
               @binding.json
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
               az stream-analytics function delete --resource-group "sjrg1637" --job-name "sj8653" \\
               --name "function8197"
"""

helps['stream-analytics function show'] = """
    type: command
    short-summary: Gets details about the specified function.
    examples:
      - name: Get details about a function
        text: |-
               az stream-analytics function show --resource-group "sjrg1637" --job-name "sj8653" --name \\
               "function8197"
"""

helps['stream-analytics function list'] = """
    type: command
    short-summary: Lists all of the functions under the specified streaming job.
    examples:
      - name: List all functions in a streaming job
        text: |-
               az stream-analytics function list --resource-group "sjrg1637" --job-name "sj8653"
"""

helps['stream-analytics function test'] = """
    type: command
    short-summary: Tests if the information provided for a function is valid.
    examples:
      - name: Test the connection for a function
        text: |-
               az stream-analytics function test --resource-group "sjrg7" --job-name "sj9093" --name \\
               "function588"
"""

helps['stream-analytics quota'] = """
    type: group
    short-summary: Commands to show quota information.
"""

helps['stream-analytics quota show'] = """
    type: command
    short-summary: Retrieves quota information in a particular region.
    examples:
      - name: List subscription quota information in West US
        text: |-
               az stream-analytics quota show --location "West US"
"""
