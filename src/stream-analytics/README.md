# Azure CLI stream-analytics Extension #
This package is for the 'stream-analytics' extension, i.e. 'az stream-analytics'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name stream-analytics
```

### Included Features
#### Stream Analytics Management:
Manage Stream Analytics: [more info](https://docs.microsoft.com/en-us/azure/stream-analytics/)\
*Examples:*

##### Create a Stream Analytics Job

```
az stream-analytics job create \
    --resource-group groupName \
    --name jobName \
    --location localtionName
```

##### Create a Stream Analytics Transformation
```
az stream-analytics transformation create \
    --resource-group groupName \
    --job-name jobName \
    --name transformationName \
    --streaming-units 3 \
    --transformation-query "SELECT * INTO outputName FROM inputName"
```

##### Create a Stream Analytics Input
```
az stream-analytics input create \
    --resource-group groupName \
    --job-name jobName \
    --name inputName \
    --type Stream \
    --datasource @datasource.json \
    --serialization @serialization.json
```
datasource.json contains the following content
```json
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
```
serialization.json contains the following content
```json
{
    "type": "Csv",
    "properties": {
        "fieldDelimiter": ",",
        "encoding": "UTF8"
    }
}
```

##### Test a Stream Analytics Input
```
az stream-analytics input test \
    --resource-group groupName \
    --job-name jobName \
    --name inputName
```

##### Create a Stream Analytics Output
```
az stream-analytics output create \
    --resource-group groupName \
    --job-name jobName \
    --name outputName \
    --datasource @datasource.json \
    --serialization @serialization.json
```
datasource.json contains the following content
```json
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
```
serialization.json contains the following content
```json
{
    "type": "Json",
    "properties": {
        "encoding": "UTF8",
        "format": "Array"
    }
}
```

##### Test a Stream Analytics Output
```
az stream-analytics output test \
    --resource-group groupName \
    --job-name jobName \
    --name outputName
```

##### Start a Stream Analytics Job
```
az stream-analytics job start \
    --resource-group groupName \
    --name jobName
```

##### Stop a Stream Analytics Job
```
az stream-analytics job stop \
    --resource-group groupName \
    --name jobName
```

##### Create a Stream Analytics Function
```
az stream-analytics function create \
    --resource-group groupName \
    --job-name jobName \
    --name functionName \
    --inputs @inputs.json \
    --function-output @function_output.json \
    --binding @binding.json
```
inputs.json contains the following content
```json
[
    {
        "dataType": "Any"
    }
]
```
function_output.json contains the following content
```json
{
    "dataType": "Any"
}
```
binding.json contains the following content
```json
{
    "type": "Microsoft.StreamAnalytics/JavascriptUdf",
    "properties": {
        "script": "function (x, y) { return x + y; }"
    }
}
```

##### Test a Stream Analytics Function
```
az stream-analytics function test \
    --resource-group groupName \
    --job-name jobName \
    --name functionName
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
