# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['stream-analytics'] = '''
    type: group
    short-summary: Manage Stream Analytics
'''

helps['stream-analytics job'] = """
    type: group
    short-summary: Manage streaming job with stream analytics
"""

helps['stream-analytics job list'] = """
    type: command
    short-summary: "List all of the streaming jobs in the specified resource group. And Lists all of the streaming \
jobs in the given subscription."
    examples:
      - name: List all streaming jobs in a resource group and do not use the $expand OData query parameter
        text: |-
               az stream-analytics job list --resource-group "sjrg6936"
      - name: List all streaming jobs in a resource group and use the $expand OData query parameter to expand inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job list --expand "inputs,outputs,transformation,functions" --resource-group \
"sjrg3276"
      - name: List all streaming jobs in a subscription and do not use the $expand OData query parameter
        text: |-
               az stream-analytics job list
      - name: List all streaming jobs in a subscription and use the $expand OData query parameter to expand inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job list --expand "inputs,outputs,transformation,functions"
"""

helps['stream-analytics job show'] = """
    type: command
    short-summary: "Get details about the specified streaming job."
    examples:
      - name: Get a streaming job and do not use the $expand OData query parameter
        text: |-
               az stream-analytics job show --job-name "sj59" --resource-group "sjrg6936"
      - name: Get a streaming job and use the $expand OData query parameter to expand inputs, outputs, transformation, and functions
        text: |-
               az stream-analytics job show --expand "inputs,outputs,transformation,functions" --job-name "sj7804" \
--resource-group "sjrg3276"
"""

helps['stream-analytics job create'] = """
    type: command
    short-summary: "Create a streaming job or replaces an already existing streaming job."
    parameters:
      - name: --identity
        short-summary: "Describe the system-assigned managed identity assigned to this job that can be used to \
authenticate with inputs and outputs."
        long-summary: |
            Usage: --identity tenant-id=XX principal-id=XX type=XX

            tenant-id: The identity tenantId
            principal-id: The identity principal ID
            type: The identity type
      - name: --transformation
        short-summary: "Indicate the query and the number of streaming units to use for the streaming job. The name \
property of the transformation is required when specifying this property in a PUT request. This property cannot be \
modify via a PATCH operation. You must use the PATCH API available for the individual transformation."
        long-summary: |
            Usage: --transformation streaming-units=XX valid-streaming-units=XX query=XX name=XX

            streaming-units: Specifies the number of streaming units that the streaming job uses.
            valid-streaming-units: Specifies the valid streaming units a streaming job can scale to.
            query: Specifies the query that will be run in the streaming job. You can learn more about the Stream \
Analytics Query Language (SAQL) here: https://msdn.microsoft.com/library/azure/dn834998 . Required on PUT \
(CreateOrReplace) requests.
            name: Resource name
      - name: --job-storage-account
        short-summary: "The properties that are associated with an Azure Storage account with MSI"
        long-summary: |
            Usage: --job-storage-account authentication-mode=XX account-name=XX account-key=XX

            authentication-mode: Authentication Mode.
            account-name: The name of the Azure Storage account. Required on PUT (CreateOrReplace) requests.
            account-key: The account key for the Azure Storage account. Required on PUT (CreateOrReplace) requests.
    examples:
      - name: Create a complete streaming job (a streaming job with a transformation, at least 1 input and at least 1 output)
        text: |-
               az stream-analytics job create --job-name "sj7804" --resource-group "sjrg3276" --location "West US" \
--compatibility-level "1.0" --data-locale "en-US" --arrival-max-delay 5 --order-max-delay 0 --out-of-order-policy \
"Drop" --functions "[]" --inputs "[{\\"name\\":\\"inputtest\\",\\"properties\\":{\\"type\\":\\"Stream\\",\\"datasource\
\\":{\\"type\\":\\"Microsoft.Storage/Blob\\",\\"properties\\":{\\"container\\":\\"containerName\\",\\"pathPattern\\":\\\
"\\",\\"storageAccounts\\":[{\\"accountKey\\":\\"yourAccountKey==\\",\\"accountName\\":\\"yourAccountName\\"}]}},\\"ser\
ialization\\":{\\"type\\":\\"Json\\",\\"properties\\":{\\"encoding\\":\\"UTF8\\"}}}}]" --output-error-policy "Drop" \
--outputs "[{\\"name\\":\\"outputtest\\",\\"datasource\\":{\\"type\\":\\"Microsoft.Sql/Server/Database\\",\\"properties\
\\":{\\"database\\":\\"databaseName\\",\\"password\\":\\"userPassword\\",\\"server\\":\\"serverName\\",\\"table\\":\\"t\
ableName\\",\\"user\\":\\"<user>\\"}}}]" --transformation name="transformationtest" streaming-units=1 query="Select \
Id, Name from inputtest" --tags key1="value1" key3="value3" randomKey="randomValue"
      - name: Create a streaming job shell (a streaming job with no inputs, outputs, transformation, or functions)
        text: |-
               az stream-analytics job create --job-name "sj59" --resource-group "sjrg6936" --location "West US" \
--compatibility-level "1.0" --data-locale "en-US" --arrival-max-delay 16 --order-max-delay 5 --out-of-order-policy \
"Drop" --functions "[]" --inputs "[]" --output-error-policy "Drop" --outputs "[]" --tags key1="value1" key3="value3" \
randomKey="randomValue"
"""

helps['stream-analytics job update'] = """
    type: command
    short-summary: "Update an existing streaming job. This can be used to partially update (ie. update one or two \
properties) a streaming job without affecting the rest the job definition."
    parameters:
      - name: --identity
        short-summary: "Describe the system-assigned managed identity assigned to this job that can be used to \
authenticate with inputs and outputs."
        long-summary: |
            Usage: --identity tenant-id=XX principal-id=XX type=XX

            tenant-id: The identity tenantId
            principal-id: The identity principal ID
            type: The identity type
      - name: --transformation
        short-summary: "Indicate the query and the number of streaming units to use for the streaming job. The name \
property of the transformation is required when specifying this property in a PUT request. This property cannot be \
modify via a PATCH operation. You must use the PATCH API available for the individual transformation."
        long-summary: |
            Usage: --transformation streaming-units=XX valid-streaming-units=XX query=XX name=XX

            streaming-units: Specifies the number of streaming units that the streaming job uses.
            valid-streaming-units: Specifies the valid streaming units a streaming job can scale to.
            query: Specifies the query that will be run in the streaming job. You can learn more about the Stream \
Analytics Query Language (SAQL) here: https://msdn.microsoft.com/library/azure/dn834998 . Required on PUT \
(CreateOrReplace) requests.
            name: Resource name
      - name: --job-storage-account
        short-summary: "The properties that are associated with an Azure Storage account with MSI"
        long-summary: |
            Usage: --job-storage-account authentication-mode=XX account-name=XX account-key=XX

            authentication-mode: Authentication Mode.
            account-name: The name of the Azure Storage account. Required on PUT (CreateOrReplace) requests.
            account-key: The account key for the Azure Storage account. Required on PUT (CreateOrReplace) requests.
    examples:
      - name: Update a streaming job
        text: |-
               az stream-analytics job update --job-name "sj59" --resource-group "sjrg6936" --arrival-max-delay 13 \
--order-max-delay 21
"""

helps['stream-analytics job delete'] = """
    type: command
    short-summary: "Delete a streaming job."
    examples:
      - name: Delete a streaming job
        text: |-
               az stream-analytics job delete --job-name "sj59" --resource-group "sjrg6936"
"""

helps['stream-analytics job scale'] = """
    type: command
    short-summary: "Scale a streaming job when the job is running."
    examples:
      - name: Scale a streaming job
        text: |-
               az stream-analytics job scale --job-name "sj59" --resource-group "sjrg6936" --streaming-units 36
"""

helps['stream-analytics job start'] = """
    type: command
    short-summary: "Start a streaming job. Once a job is started it will start processing input events and produce \
output."
    examples:
      - name: Start a streaming job with CustomTime output start mode
        text: |-
               az stream-analytics job start --job-name "sj59" --resource-group "sjrg6936" --output-start-mode \
"CustomTime" --output-start-time "2012-12-12T12:12:12Z"
      - name: Start a streaming job with JobStartTime output start mode
        text: |-
               az stream-analytics job start --job-name "sj59" --resource-group "sjrg6936" --output-start-mode \
"JobStartTime"
      - name: Start a streaming job with LastOutputEventTime output start mode
        text: |-
               az stream-analytics job start --job-name "sj59" --resource-group "sjrg6936" --output-start-mode \
"LastOutputEventTime"
"""

helps['stream-analytics job stop'] = """
    type: command
    short-summary: "Stop a running streaming job. This will cause a running streaming job to stop processing input \
events and producing output."
    examples:
      - name: Stop a streaming job
        text: |-
               az stream-analytics job stop --job-name "sj59" --resource-group "sjrg6936"
"""

helps['stream-analytics job wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics job is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics job is successfully created.
        text: |-
               az stream-analytics job wait --expand "inputs,outputs,transformation,functions" --job-name "sj7804" \
--resource-group "sjrg3276" --created
      - name: Pause executing next line of CLI script until the stream-analytics job is successfully deleted.
        text: |-
               az stream-analytics job wait --expand "inputs,outputs,transformation,functions" --job-name "sj7804" \
--resource-group "sjrg3276" --deleted
"""

helps['stream-analytics input'] = """
    type: group
    short-summary: Manage input with stream analytics
"""

helps['stream-analytics input list'] = """
    type: command
    short-summary: "List all of the inputs under the specified streaming job."
    examples:
      - name: List all inputs in a streaming job
        text: |-
               az stream-analytics input list --job-name "sj9597" --resource-group "sjrg8440"
      - name: List all inputs in a streaming job and include diagnostic information using the $select OData query parameter
        text: |-
               az stream-analytics input list --select "*" --job-name "sj7804" --resource-group "sjrg3276"
"""

helps['stream-analytics input show'] = """
    type: command
    short-summary: "Get details about the specified input."
    examples:
      - name: Get a reference blob input with CSV serialization
        text: |-
               az stream-analytics input show --input-name "input7225" --job-name "sj9597" --resource-group "sjrg8440"
      - name: Get a stream Event Hub input with JSON serialization
        text: |-
               az stream-analytics input show --input-name "input7425" --job-name "sj197" --resource-group "sjrg3139"
      - name: Get a stream IoT Hub input with Avro serialization
        text: |-
               az stream-analytics input show --input-name "input7970" --job-name "sj9742" --resource-group "sjrg3467"
      - name: Get a stream blob input with CSV serialization
        text: |-
               az stream-analytics input show --input-name "input8899" --job-name "sj6695" --resource-group "sjrg8161"
"""

helps['stream-analytics input create'] = """
    type: command
    short-summary: "Create an input or replaces an already existing input under an existing streaming job."
    examples:
      - name: Create a reference blob input with CSV serialization
        text: |-
               az stream-analytics input create --properties "{\\"type\\":\\"Reference\\",\\"datasource\\":{\\"type\\":\
\\"Microsoft.Storage/Blob\\",\\"properties\\":{\\"container\\":\\"state\\",\\"dateFormat\\":\\"yyyy/MM/dd\\",\\"pathPat\
tern\\":\\"{date}/{time}\\",\\"storageAccounts\\":[{\\"accountKey\\":\\"someAccountKey==\\",\\"accountName\\":\\"someAc\
countName\\"}],\\"timeFormat\\":\\"HH\\"}},\\"serialization\\":{\\"type\\":\\"Csv\\",\\"properties\\":{\\"encoding\\":\
\\"UTF8\\",\\"fieldDelimiter\\":\\",\\"}}}" --input-name "input7225" --job-name "sj9597" --resource-group "sjrg8440"
      - name: Create a stream Event Hub input with JSON serialization
        text: |-
               az stream-analytics input create --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.ServiceBus/EventHub\\",\\"properties\\":{\\"consumerGroupName\\":\\"sdkconsumergroup\\",\\"eventHubName\\":\\\
"sdkeventhub\\",\\"serviceBusNamespace\\":\\"sdktest\\",\\"sharedAccessPolicyKey\\":\\"someSharedAccessPolicyKey==\\",\
\\"sharedAccessPolicyName\\":\\"RootManageSharedAccessKey\\"}},\\"serialization\\":{\\"type\\":\\"Json\\",\\"properties\
\\":{\\"encoding\\":\\"UTF8\\"}}}" --input-name "input7425" --job-name "sj197" --resource-group "sjrg3139"
      - name: Create a stream IoT Hub input with Avro serialization
        text: |-
               az stream-analytics input create --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.Devices/IotHubs\\",\\"properties\\":{\\"consumerGroupName\\":\\"sdkconsumergroup\\",\\"endpoint\\":\\"message\
s/events\\",\\"iotHubNamespace\\":\\"iothub\\",\\"sharedAccessPolicyKey\\":\\"sharedAccessPolicyKey=\\",\\"sharedAccess\
PolicyName\\":\\"owner\\"}},\\"serialization\\":{\\"type\\":\\"Avro\\"}}" --input-name "input7970" --job-name "sj9742" \
--resource-group "sjrg3467"
      - name: Create a stream blob input with CSV serialization
        text: |-
               az stream-analytics input create --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.Storage/Blob\\",\\"properties\\":{\\"container\\":\\"state\\",\\"dateFormat\\":\\"yyyy/MM/dd\\",\\"pathPatter\
n\\":\\"{date}/{time}\\",\\"sourcePartitionCount\\":16,\\"storageAccounts\\":[{\\"accountKey\\":\\"someAccountKey==\\",\
\\"accountName\\":\\"someAccountName\\"}],\\"timeFormat\\":\\"HH\\"}},\\"serialization\\":{\\"type\\":\\"Csv\\",\\"prop\
erties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\",\\"}}}" --input-name "input8899" --job-name "sj6695" \
--resource-group "sjrg8161"
"""

helps['stream-analytics input update'] = """
    type: command
    short-summary: "Update an existing input under an existing streaming job. This can be used to partially update \
(ie. update one or two properties) an input without affecting the rest the job or input definition."
    examples:
      - name: Update a reference blob input
        text: |-
               az stream-analytics input update --properties "{\\"type\\":\\"Reference\\",\\"datasource\\":{\\"type\\":\
\\"Microsoft.Storage/Blob\\",\\"properties\\":{\\"container\\":\\"differentContainer\\"}},\\"serialization\\":{\\"type\
\\":\\"Csv\\",\\"properties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\"|\\"}}}" --input-name "input7225" \
--job-name "sj9597" --resource-group "sjrg8440"
      - name: Update a stream Event Hub input
        text: |-
               az stream-analytics input update --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.ServiceBus/EventHub\\",\\"properties\\":{\\"consumerGroupName\\":\\"differentConsumerGroupName\\"}},\\"serial\
ization\\":{\\"type\\":\\"Avro\\"}}" --input-name "input7425" --job-name "sj197" --resource-group "sjrg3139"
      - name: Update a stream IoT Hub input
        text: |-
               az stream-analytics input update --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.Devices/IotHubs\\",\\"properties\\":{\\"endpoint\\":\\"messages/operationsMonitoringEvents\\"}},\\"serializat\
ion\\":{\\"type\\":\\"Csv\\",\\"properties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\"|\\"}}}" --input-name \
"input7970" --job-name "sj9742" --resource-group "sjrg3467"
      - name: Update a stream blob input
        text: |-
               az stream-analytics input update --properties "{\\"type\\":\\"Stream\\",\\"datasource\\":{\\"type\\":\\"\
Microsoft.Storage/Blob\\",\\"properties\\":{\\"sourcePartitionCount\\":32}},\\"serialization\\":{\\"type\\":\\"Csv\\",\
\\"properties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\"|\\"}}}" --input-name "input8899" --job-name \
"sj6695" --resource-group "sjrg8161"
"""

helps['stream-analytics input delete'] = """
    type: command
    short-summary: "Delete an input from the streaming job."
    examples:
      - name: Delete an input
        text: |-
               az stream-analytics input delete --input-name "input7225" --job-name "sj9597" --resource-group \
"sjrg8440"
"""

helps['stream-analytics input test'] = """
    type: command
    short-summary: "Test whether an input’s datasource is reachable and usable by the Azure Stream Analytics \
service."
    examples:
      - name: Test the connection for an input
        text: |-
               az stream-analytics input test --input-name "input7225" --job-name "sj9597" --resource-group "sjrg8440"
"""

helps['stream-analytics input wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics input is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics input is successfully created.
        text: |-
               az stream-analytics input wait --input-name "input8899" --job-name "sj6695" --resource-group "sjrg8161" \
--created
"""

helps['stream-analytics output'] = """
    type: group
    short-summary: Manage output with stream analytics
"""

helps['stream-analytics output list'] = """
    type: command
    short-summary: "List all of the outputs under the specified streaming job."
    examples:
      - name: List all outputs in a streaming job
        text: |-
               az stream-analytics output list --job-name "sj6458" --resource-group "sjrg2157"
"""

helps['stream-analytics output show'] = """
    type: command
    short-summary: "Get details about the specified output."
    examples:
      - name: Get a DocumentDB output
        text: |-
               az stream-analytics output show --job-name "sj2331" --output-name "output3022" --resource-group \
"sjrg7983"
      - name: Get a Power BI output
        text: |-
               az stream-analytics output show --job-name "sj2331" --output-name "output3022" --resource-group \
"sjrg7983"
      - name: Get a Service Bus Queue output with Avro serialization
        text: |-
               az stream-analytics output show --job-name "sj5095" --output-name "output3456" --resource-group \
"sjrg3410"
      - name: Get a Service Bus Topic output with CSV serialization
        text: |-
               az stream-analytics output show --job-name "sj7094" --output-name "output7886" --resource-group \
"sjrg6450"
      - name: Get a blob output with CSV serialization
        text: |-
               az stream-analytics output show --job-name "sj900" --output-name "output1623" --resource-group \
"sjrg5023"
      - name: Get an Azure Data Lake Store output with JSON serialization
        text: |-
               az stream-analytics output show --job-name "sj3310" --output-name "output5195" --resource-group \
"sjrg6912"
      - name: Get an Azure Data Warehouse output
        text: |-
               az stream-analytics output show --job-name "sjName" --output-name "output958" --resource-group "sjrg"
      - name: Get an Azure SQL database output
        text: |-
               az stream-analytics output show --job-name "sj6458" --output-name "output1755" --resource-group \
"sjrg2157"
      - name: Get an Azure Table output
        text: |-
               az stream-analytics output show --job-name "sj2790" --output-name "output958" --resource-group \
"sjrg5176"
      - name: Get an Event Hub output with JSON serialization
        text: |-
               az stream-analytics output show --job-name "sj3310" --output-name "output5195" --resource-group \
"sjrg6912"
"""

helps['stream-analytics output create'] = """
    type: command
    short-summary: "Create an output or replaces an already existing output under an existing streaming job."
    examples:
      - name: Create a DocumentDB output
        text: |-
               az stream-analytics output create --job-name "sj2331" --datasource "{\\"type\\":\\"Microsoft.Storage/Doc\
umentDB\\",\\"properties\\":{\\"accountId\\":\\"someAccountId\\",\\"accountKey\\":\\"accountKey==\\",\\"collectionNameP\
attern\\":\\"collection\\",\\"database\\":\\"db01\\",\\"documentId\\":\\"documentId\\",\\"partitionKey\\":\\"key\\"}}" \
--output-name "output3022" --resource-group "sjrg7983"
      - name: Create a Power BI output
        text: |-
               az stream-analytics output create --job-name "sj2331" --datasource "{\\"type\\":\\"PowerBI\\",\\"propert\
ies\\":{\\"dataset\\":\\"someDataset\\",\\"groupId\\":\\"ac40305e-3e8d-43ac-8161-c33799f43e95\\",\\"groupName\\":\\"MyP\
owerBIGroup\\",\\"refreshToken\\":\\"someRefreshToken==\\",\\"table\\":\\"someTable\\",\\"tokenUserDisplayName\\":\\"Bo\
b Smith\\",\\"tokenUserPrincipalName\\":\\"bobsmith@contoso.com\\"}}" --output-name "output3022" --resource-group \
"sjrg7983"
      - name: Create a Service Bus Queue output with Avro serialization
        text: |-
               az stream-analytics output create --job-name "sj5095" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
Queue\\",\\"properties\\":{\\"propertyColumns\\":[\\"column1\\",\\"column2\\"],\\"queueName\\":\\"sdkqueue\\",\\"servic\
eBusNamespace\\":\\"sdktest\\",\\"sharedAccessPolicyKey\\":\\"sharedAccessPolicyKey=\\",\\"sharedAccessPolicyName\\":\\\
"RootManageSharedAccessKey\\",\\"systemPropertyColumns\\":{\\"MessageId\\":\\"col3\\",\\"PartitionKey\\":\\"col4\\"}}}"\
 --serialization "{\\"type\\":\\"Avro\\"}" --output-name "output3456" --resource-group "sjrg3410"
      - name: Create a Service Bus Topic output with CSV serialization
        text: |-
               az stream-analytics output create --job-name "sj7094" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
Topic\\",\\"properties\\":{\\"propertyColumns\\":[\\"column1\\",\\"column2\\"],\\"serviceBusNamespace\\":\\"sdktest\\",\
\\"sharedAccessPolicyKey\\":\\"sharedAccessPolicyKey=\\",\\"sharedAccessPolicyName\\":\\"RootManageSharedAccessKey\\",\
\\"topicName\\":\\"sdktopic\\"}}" --serialization "{\\"type\\":\\"Csv\\",\\"properties\\":{\\"encoding\\":\\"UTF8\\",\\\
"fieldDelimiter\\":\\",\\"}}" --output-name "output7886" --resource-group "sjrg6450"
      - name: Create a blob output with CSV serialization
        text: |-
               az stream-analytics output create --job-name "sj900" --datasource "{\\"type\\":\\"Microsoft.Storage/Blob\
\\",\\"properties\\":{\\"container\\":\\"state\\",\\"dateFormat\\":\\"yyyy/MM/dd\\",\\"pathPattern\\":\\"{date}/{time}\
\\",\\"storageAccounts\\":[{\\"accountKey\\":\\"accountKey==\\",\\"accountName\\":\\"someAccountName\\"}],\\"timeFormat\
\\":\\"HH\\"}}" --serialization "{\\"type\\":\\"Csv\\",\\"properties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\"\
:\\",\\"}}" --output-name "output1623" --resource-group "sjrg5023"
      - name: Create an Azure Data Lake Store output with JSON serialization
        text: |-
               az stream-analytics output create --job-name "sj3310" --datasource "{\\"type\\":\\"Microsoft.DataLake/Ac\
counts\\",\\"properties\\":{\\"accountName\\":\\"someaccount\\",\\"dateFormat\\":\\"yyyy/MM/dd\\",\\"filePathPrefix\\":\
\\"{date}/{time}\\",\\"refreshToken\\":\\"someRefreshToken==\\",\\"tenantId\\":\\"cea4e98b-c798-49e7-8c40-4a2b3beb47dd\
\\",\\"timeFormat\\":\\"HH\\",\\"tokenUserDisplayName\\":\\"Bob Smith\\",\\"tokenUserPrincipalName\\":\\"bobsmith@conto\
so.com\\"}}" --serialization "{\\"type\\":\\"Json\\",\\"properties\\":{\\"format\\":\\"Array\\",\\"encoding\\":\\"UTF8\
\\"}}" --output-name "output5195" --resource-group "sjrg6912"
      - name: Create an Azure SQL database output
        text: |-
               az stream-analytics output create --job-name "sj6458" --datasource "{\\"type\\":\\"Microsoft.Sql/Server/\
Database\\",\\"properties\\":{\\"database\\":\\"someDatabase\\",\\"password\\":\\"somePassword\\",\\"server\\":\\"someS\
erver\\",\\"table\\":\\"someTable\\",\\"user\\":\\"<user>\\"}}" --output-name "output1755" --resource-group "sjrg2157"
      - name: Create an Azure Table output
        text: |-
               az stream-analytics output create --job-name "sj2790" --datasource "{\\"type\\":\\"Microsoft.Storage/Tab\
le\\",\\"properties\\":{\\"accountKey\\":\\"accountKey==\\",\\"accountName\\":\\"someAccountName\\",\\"batchSize\\":25,\
\\"columnsToRemove\\":[\\"column1\\",\\"column2\\"],\\"partitionKey\\":\\"partitionKey\\",\\"rowKey\\":\\"rowKey\\",\\"\
table\\":\\"samples\\"}}" --output-name "output958" --resource-group "sjrg5176"
      - name: Create an Event Hub output with JSON serialization
        text: |-
               az stream-analytics output create --job-name "sj3310" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
EventHub\\",\\"properties\\":{\\"eventHubName\\":\\"sdkeventhub\\",\\"partitionKey\\":\\"partitionKey\\",\\"serviceBusN\
amespace\\":\\"sdktest\\",\\"sharedAccessPolicyKey\\":\\"sharedAccessPolicyKey=\\",\\"sharedAccessPolicyName\\":\\"Root\
ManageSharedAccessKey\\"}}" --serialization "{\\"type\\":\\"Json\\",\\"properties\\":{\\"format\\":\\"Array\\",\\"encod\
ing\\":\\"UTF8\\"}}" --output-name "output5195" --resource-group "sjrg6912"
"""

helps['stream-analytics output update'] = """
    type: command
    short-summary: "Update an existing output under an existing streaming job. This can be used to partially update \
(ie. update one or two properties) an output without affecting the rest the job or output definition."
    examples:
      - name: Update a DocumentDB output
        text: |-
               az stream-analytics output update --job-name "sj2331" --datasource "{\\"type\\":\\"Microsoft.Storage/Doc\
umentDB\\",\\"properties\\":{\\"partitionKey\\":\\"differentPartitionKey\\"}}" --output-name "output3022" \
--resource-group "sjrg7983"
      - name: Update a Power BI output
        text: |-
               az stream-analytics output update --job-name "sj2331" --datasource "{\\"type\\":\\"PowerBI\\",\\"propert\
ies\\":{\\"dataset\\":\\"differentDataset\\"}}" --output-name "output3022" --resource-group "sjrg7983"
      - name: Update a Service Bus Queue output with Avro serialization
        text: |-
               az stream-analytics output update --job-name "sj5095" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
Queue\\",\\"properties\\":{\\"queueName\\":\\"differentQueueName\\"}}" --serialization "{\\"type\\":\\"Json\\",\\"prope\
rties\\":{\\"format\\":\\"LineSeparated\\",\\"encoding\\":\\"UTF8\\"}}" --output-name "output3456" --resource-group \
"sjrg3410"
      - name: Update a Service Bus Topic output with CSV serialization
        text: |-
               az stream-analytics output update --job-name "sj7094" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
Topic\\",\\"properties\\":{\\"topicName\\":\\"differentTopicName\\"}}" --serialization "{\\"type\\":\\"Csv\\",\\"proper\
ties\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\"|\\"}}" --output-name "output7886" --resource-group \
"sjrg6450"
      - name: Update a blob output with CSV serialization
        text: |-
               az stream-analytics output update --job-name "sj900" --datasource "{\\"type\\":\\"Microsoft.Storage/Blob\
\\",\\"properties\\":{\\"container\\":\\"differentContainer\\"}}" --serialization "{\\"type\\":\\"Csv\\",\\"properties\
\\":{\\"encoding\\":\\"UTF8\\",\\"fieldDelimiter\\":\\"|\\"}}" --output-name "output1623" --resource-group "sjrg5023"
      - name: Update an Azure Data Lake Store output with JSON serialization
        text: |-
               az stream-analytics output update --job-name "sj3310" --datasource "{\\"type\\":\\"Microsoft.DataLake/Ac\
counts\\",\\"properties\\":{\\"accountName\\":\\"differentaccount\\"}}" --serialization "{\\"type\\":\\"Json\\",\\"prop\
erties\\":{\\"format\\":\\"LineSeparated\\",\\"encoding\\":\\"UTF8\\"}}" --output-name "output5195" --resource-group \
"sjrg6912"
      - name: Update an Azure SQL database output
        text: |-
               az stream-analytics output update --job-name "sj6458" --datasource "{\\"type\\":\\"Microsoft.Sql/Server/\
Database\\",\\"properties\\":{\\"table\\":\\"differentTable\\"}}" --output-name "output1755" --resource-group \
"sjrg2157"
      - name: Update an Azure Table output
        text: |-
               az stream-analytics output update --job-name "sj2790" --datasource "{\\"type\\":\\"Microsoft.Storage/Tab\
le\\",\\"properties\\":{\\"partitionKey\\":\\"differentPartitionKey\\"}}" --output-name "output958" --resource-group \
"sjrg5176"
      - name: Update an Event Hub output with JSON serialization
        text: |-
               az stream-analytics output update --job-name "sj3310" --datasource "{\\"type\\":\\"Microsoft.ServiceBus/\
EventHub\\",\\"properties\\":{\\"partitionKey\\":\\"differentPartitionKey\\"}}" --serialization \
"{\\"type\\":\\"Json\\",\\"properties\\":{\\"format\\":\\"LineSeparated\\",\\"encoding\\":\\"UTF8\\"}}" --output-name \
"output5195" --resource-group "sjrg6912"
"""

helps['stream-analytics output delete'] = """
    type: command
    short-summary: "Delete an output from the streaming job."
    examples:
      - name: Delete an output
        text: |-
               az stream-analytics output delete --job-name "sj6458" --name "output1755" --resource-group "sjrg2157"
"""

helps['stream-analytics output test'] = """
    type: command
    short-summary: "Test whether an output’s datasource is reachable and usable by the Azure Stream Analytics \
service."
    examples:
      - name: Test the connection for an output
        text: |-
               az stream-analytics output test --job-name "sj6458" --output-name "output1755" --resource-group \
"sjrg2157"
"""

helps['stream-analytics output wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics output is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics output is successfully created.
        text: |-
               az stream-analytics output wait --job-name "sj3310" --output-name "output5195" --resource-group \
"sjrg6912" --created
"""

helps['stream-analytics transformation'] = """
    type: group
    short-summary: Manage transformation with stream analytics
"""

helps['stream-analytics transformation show'] = """
    type: command
    short-summary: "Get details about the specified transformation."
    examples:
      - name: Get a transformation
        text: |-
               az stream-analytics transformation show --job-name "sj8374" --resource-group "sjrg4423" --name \
"transformation952"
"""

helps['stream-analytics transformation create'] = """
    type: command
    short-summary: "Create a transformation or replaces an already existing transformation under an existing \
streaming job."
    examples:
      - name: Create a transformation
        text: |-
               az stream-analytics transformation create --job-name "sj8374" --resource-group "sjrg4423" --saql \
"Select Id, Name from inputtest" --streaming-units 6 --transformation-name "transformation952"
"""

helps['stream-analytics transformation update'] = """
    type: command
    short-summary: "Update an existing transformation under an existing streaming job. This can be used to partially \
update (ie. update one or two properties) a transformation without affecting the rest the job or transformation \
definition."
    examples:
      - name: Update a transformation
        text: |-
               az stream-analytics transformation update --job-name "sj8374" --resource-group "sjrg4423" --saql "New \
query" --transformation-name "transformation952"
"""

helps['stream-analytics function'] = """
    type: group
    short-summary: Manage function with stream analytics
"""

helps['stream-analytics function list'] = """
    type: command
    short-summary: "List all of the functions under the specified streaming job."
    examples:
      - name: List all functions in a streaming job
        text: |-
               az stream-analytics function list --job-name "sj8653" --resource-group "sjrg1637"
"""

helps['stream-analytics function show'] = """
    type: command
    short-summary: "Get details about the specified function."
    examples:
      - name: Get a JavaScript function
        text: |-
               az stream-analytics function show --name "function8197" --job-name "sj8653" --resource-group "sjrg1637"
      - name: Get an Azure ML function
        text: |-
               az stream-analytics function show --name "function588" --job-name "sj9093" --resource-group "sjrg7"
"""

helps['stream-analytics function create'] = """
    type: command
    short-summary: "Create a function or replaces an already existing function under an existing streaming job."
    examples:
      - name: Create a JavaScript function
        text: |-
               az stream-analytics function create --properties "{\\"type\\":\\"Scalar\\",\\"properties\\":{\\"binding\
\\":{\\"type\\":\\"Microsoft.StreamAnalytics/JavascriptUdf\\",\\"properties\\":{\\"script\\":\\"function (x, y) { \
return x + y; }\\"}},\\"inputs\\":[{\\"dataType\\":\\"Any\\"}],\\"output\\":{\\"dataType\\":\\"Any\\"}}}" \
--function-name "function8197" --job-name "sj8653" --resource-group "sjrg1637"
      - name: Create an Azure ML function
        text: |-
               az stream-analytics function create --properties "{\\"type\\":\\"Scalar\\",\\"properties\\":{\\"binding\
\\":{\\"type\\":\\"Microsoft.MachineLearning/WebService\\",\\"properties\\":{\\"apiKey\\":\\"someApiKey==\\",\\"batchSi\
ze\\":1000,\\"endpoint\\":\\"someAzureMLEndpointURL\\",\\"inputs\\":{\\"name\\":\\"input1\\",\\"columnNames\\":[{\\"nam\
e\\":\\"tweet\\",\\"dataType\\":\\"string\\",\\"mapTo\\":0}]},\\"outputs\\":[{\\"name\\":\\"Sentiment\\",\\"dataType\\"\
:\\"string\\"}]}},\\"inputs\\":[{\\"dataType\\":\\"nvarchar(max)\\"}],\\"output\\":{\\"dataType\\":\\"nvarchar(max)\\"}\
}}" --function-name "function588" --job-name "sj9093" --resource-group "sjrg7"
"""

helps['stream-analytics function update'] = """
    type: command
    short-summary: "Update an existing function under an existing streaming job. This can be used to partially update \
(ie. update one or two properties) a function without affecting the rest the job or function definition."
    examples:
      - name: Update a JavaScript function
        text: |-
               az stream-analytics function update --properties "{\\"type\\":\\"Scalar\\",\\"properties\\":{\\"binding\
\\":{\\"type\\":\\"Microsoft.StreamAnalytics/JavascriptUdf\\",\\"properties\\":{\\"script\\":\\"function (a, b) { \
return a * b; }\\"}}}}" --function-name "function8197" --job-name "sj8653" --resource-group "sjrg1637"
      - name: Update an Azure ML function
        text: |-
               az stream-analytics function update --properties "{\\"type\\":\\"Scalar\\",\\"properties\\":{\\"binding\
\\":{\\"type\\":\\"Microsoft.MachineLearning/WebService\\",\\"properties\\":{\\"batchSize\\":5000}}}}" --function-name \
"function588" --job-name "sj9093" --resource-group "sjrg7"
"""

helps['stream-analytics function delete'] = """
    type: command
    short-summary: "Delete a function from the streaming job."
    examples:
      - name: Delete a function
        text: |-
               az stream-analytics function delete --name "function8197" --job-name "sj8653" --resource-group \
"sjrg1637"
"""

helps['stream-analytics function inspect'] = """
    type: command
    short-summary: "Retrieve the default definition of a function based on the parameters specified."
    parameters:
      - name: --ml-properties
        short-summary: "The parameters needed to retrieve the default function definition for an Azure Machine \
Learning web service function."
        long-summary: |
            Usage: --ml-properties execute-endpoint=XX

            execute-endpoint: The Request-Response execute endpoint of the Azure Machine Learning web service. Find \
out more here: https://docs.microsoft.com/en-us/azure/stream-analytics/machine-learning-udf
"""

helps['stream-analytics function test'] = """
    type: command
    short-summary: "Test if the information provided for a function is valid. This can range from testing the \
connection to the underlying web service behind the function or making sure the function code provided is \
syntactically correct."
    examples:
      - name: Test the connection for a JavaScript function
        text: |-
               az stream-analytics function test --function-name "function8197" --job-name "sj8653" --resource-group \
"sjrg1637"
      - name: Test the connection for an Azure ML function
        text: |-
               az stream-analytics function test --function-name "function588" --job-name "sj9093" --resource-group \
"sjrg7"
"""

helps['stream-analytics function wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics function is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics function is successfully created.
        text: |-
               az stream-analytics function wait --name "function588" --job-name "sj9093" --resource-group "sjrg7" \
--created
"""

helps['stream-analytics subscription'] = """
    type: group
    short-summary: Manage subscription with stream analytics
"""

helps['stream-analytics subscription inspect'] = """
    type: command
    short-summary: "Retrieve the subscription's current quota information in a particular region."
    examples:
      - name: List subscription quota information in West US
        text: |-
               az stream-analytics subscription inspect --location "West US"
"""

helps['stream-analytics private-endpoint'] = """
    type: group
    short-summary: Manage private endpoint with stream analytics
"""

helps['stream-analytics private-endpoint list'] = """
    type: command
    short-summary: "List the private endpoints in the cluster."
    examples:
      - name: Get the private endpoints in a cluster
        text: |-
               az stream-analytics private-endpoint list --cluster-name "testcluster" --resource-group "sjrg"
"""

helps['stream-analytics private-endpoint show'] = """
    type: command
    short-summary: "Get information about the specified Private Endpoint."
    examples:
      - name: Get a private endpoint
        text: |-
               az stream-analytics private-endpoint show --cluster-name "testcluster" --name "testpe" --resource-group \
"sjrg"
"""

helps['stream-analytics private-endpoint create'] = """
    type: command
    short-summary: "Create a Stream Analytics Private Endpoint or replaces an already existing Private Endpoint."
    examples:
      - name: Create a private endpoint
        text: |-
               az stream-analytics private-endpoint create --cluster-name "testcluster" --connections \
"[{\\"privateLinkServiceId\\":\\"/subscriptions/subId/resourceGroups/rg1/providers/Microsoft.Network/private\
LinkServices/testPls\\",\\"groupIds\\":[\\"groupIdFromResource\\"]}]" --name "testpe" --resource-group "sjrg"
"""

helps['stream-analytics private-endpoint delete'] = """
    type: command
    short-summary: "Delete the specified private endpoint."
    examples:
      - name: Delete a private endpoint
        text: |-
               az stream-analytics private-endpoint delete --cluster-name "testcluster" --name "testpe" \
--resource-group "sjrg"
"""

helps['stream-analytics private-endpoint wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics private-endpoint is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics private-endpoint is successfully \
deleted.
        text: |-
               az stream-analytics private-endpoint wait --cluster-name "testcluster" --name "testpe" --resource-group \
"sjrg" --deleted
"""

helps['stream-analytics cluster'] = """
    type: group
    short-summary: Manage cluster with stream analytics
"""

helps['stream-analytics cluster list'] = """
    type: command
    short-summary: "List all of the clusters in the given resource group. And Lists all of the clusters in the given \
subscription."
    examples:
      - name: List clusters in resource group
        text: |-
               az stream-analytics cluster list --resource-group "sjrg"
      - name: List the clusters in a subscription
        text: |-
               az stream-analytics cluster list
"""

helps['stream-analytics cluster show'] = """
    type: command
    short-summary: "Get information about the specified cluster."
    examples:
      - name: Get a cluster
        text: |-
               az stream-analytics cluster show --name "testcluster" --resource-group "sjrg"
"""

helps['stream-analytics cluster create'] = """
    type: command
    short-summary: "Create a Stream Analytics Cluster or replaces an already existing cluster."
    parameters:
      - name: --sku
        short-summary: "The SKU of the cluster. This determines the size/capacity of the cluster. Required on PUT \
(CreateOrUpdate) requests."
        long-summary: |
            Usage: --sku name=XX capacity=XX

            name: Specifies the SKU name of the cluster. Required on PUT (CreateOrUpdate) requests.
            capacity: Denotes the number of streaming units the cluster can support. Valid values for this property \
are multiples of 36 with a minimum value of 36 and maximum value of 216. Required on PUT (CreateOrUpdate) requests.
    examples:
      - name: Create a new cluster
        text: |-
               az stream-analytics cluster create --location "North US" --sku name="Default" capacity=36 --tags \
key="value" --name "An Example Cluster" --resource-group "sjrg"
"""

helps['stream-analytics cluster update'] = """
    type: command
    short-summary: "Update an existing cluster. This can be used to partially update (ie. update one or two \
properties) a cluster without affecting the rest of the cluster definition."
    parameters:
      - name: --sku
        short-summary: "The SKU of the cluster. This determines the size/capacity of the cluster. Required on PUT \
(CreateOrUpdate) requests."
        long-summary: |
            Usage: --sku name=XX capacity=XX

            name: Specifies the SKU name of the cluster. Required on PUT (CreateOrUpdate) requests.
            capacity: Denotes the number of streaming units the cluster can support. Valid values for this property \
are multiples of 36 with a minimum value of 36 and maximum value of 216. Required on PUT (CreateOrUpdate) requests.
    examples:
      - name: Update a cluster
        text: |-
               az stream-analytics cluster update --location "Central US" --sku capacity=72 --name "testcluster" \
--resource-group "sjrg"
"""

helps['stream-analytics cluster delete'] = """
    type: command
    short-summary: "Delete the specified cluster."
    examples:
      - name: Delete a cluster
        text: |-
               az stream-analytics cluster delete --name "testcluster" --resource-group "sjrg"
"""

helps['stream-analytics cluster list-streaming-job'] = """
    type: command
    short-summary: "List all of the streaming jobs in the given cluster."
    examples:
      - name: List all streaming jobs in cluster
        text: |-
               az stream-analytics cluster list-streaming-job --name "testcluster" --resource-group "sjrg"
"""

helps['stream-analytics cluster wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the stream-analytics cluster is met.
    examples:
      - name: Pause executing next line of CLI script until the stream-analytics cluster is successfully created.
        text: |-
               az stream-analytics cluster wait --name "testcluster" --resource-group "sjrg" --created
      - name: Pause executing next line of CLI script until the stream-analytics cluster is successfully updated.
        text: |-
               az stream-analytics cluster wait --name "testcluster" --resource-group "sjrg" --updated
      - name: Pause executing next line of CLI script until the stream-analytics cluster is successfully deleted.
        text: |-
               az stream-analytics cluster wait --name "testcluster" --resource-group "sjrg" --deleted
"""
