# Azure CLI automation Extension #
This package is for the 'azure data transfer' extension, i.e. 'az data-transfer'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name data-transfer
```

### Included Features
#### Viewing Pipelines:
Manage Connection: [more info](https://learn.microsoft.com/en-us/azure/templates/microsoft.azuredatatransfer/pipelines/)\
*Examples:*

##### Get a pipeline

```
az data-transfer pipeline show \
    --resource-group groupName \
    --pipeline-name pipelineName

```
##### List all pipelines in a subscription 

```
az data-transfer pipeline show --resource-group groupName

```

```
az data-transfer pipeline show

```

##### Approve a connection in a pipeline

```
az data-transfer pipeline approve-connection \
    --resource-group groupName \
    --pipeline-name pipelineName \
    --connection-id connectionResourceId

```

##### Reject a connection in a pipeline

```
az data-transfer pipeline reject-connection \
    --resource-group groupName \
    --pipeline-name pipelineName \
    --connection-id connectionResourceId

```

#### Connection Management:
Manage Connection: [more info](https://learn.microsoft.com/en-us/azure/templates/microsoft.azuredatatransfer/connections/)\
*Examples:*

##### Create a receive side connection

```
az data-transfer connection create \
    --resource-group groupName \
    --name connectionName \
    --location westus \
    --pipeline PipelineName \
    --direction Receive \
    --flow-types Api Data \
    --remote-subscription-id subscriptionId \
    --justification 'justification string' \
    --requirement-id 1234 \
    --primary-contact abc@microsoft.com \
    --secondary-contacts abc@microsoft.com

```
##### Create a send side connection

```
az data-transfer connection create \
    --resource-group groupName \
    --name connectionName \
    --location westus \
    --pipeline PipelineName \
    --direction Send \
    --flow-types Mission Data \
    --pin 123456\
    --primary-contact abc@microsoft.com \
    --secondary-contacts abc@microsoft.com

```

##### Link send and receive side connections

```
az data-transfer connection link \
    --resource-group groupName \
    --name receiveSideConnectionName \
    --pending-connection-id sendSideResourceId

```

##### List connections in a resource group

```
az data-transfer connection link \
    --resource-group groupName \
    --maxItems 10
    --nextToken <Link from previous response>

```

##### List pending connections that can be linked with the given connection

```
az data-transfer connection list-pending-connection \
    --resource-group groupName \
    --name receiveSideConnectionName \
    --maxItems 10 \
    --nextToken <Link from previous response>

```

##### List pending flows in the given connection that are not linked

```
az data-transfer connection list-pending-flow \
    --resource-group groupName \
    --connection-name receiveSideConnectionName \
    --maxItems 10 \
    --nextToken <Link from previous response>

```

##### Get the given connection

```
az data-transfer connection show \
    --resource-group groupName \
    --connection-name connectionName

```

##### Update the given connection

Update of the tags is only supported.

```
az data-transfer connection update \
    --resource-group groupName \
    --connection-name connectionName \
    --tags key1=update1

```

#### Flow Management:
Manage Flow: [more info](https://learn.microsoft.com/en-us/azure/templates/microsoft.azuredatatransfer/connections/flows/)\
*Examples:*

##### List flows in the given connection.

```
az data-transfer connection list-pending-flow \
    --resource-group groupName \
    --connection-name receiveSideConnectionName \
    --maxItems 10 \
    --nextToken <Link from previous response>

```

##### Create a flow

```

az data-transfer connection flow create \
  --resource-group resourceGroupname \
  --connection-name connectionName \
  --name flowName \
  --flow-type "Mission" \
  --location eastus \
  --status "Enabled" \
  --storage-account strorageAccountResourceId \
  --storage-container-name testContainer \
  --data-type "Blob" 

```

##### Link send and receive side flows

```
az data-transfer connection link \
    --resource-group groupName \
    --connection-name receiveSideConnectionName \
    --name receiveSideFlowName \
    --pending-flow-id sendSideFlowResourceId

```

##### Get the given flow

```
az data-transfer connection flow show \
    --resource-group groupName \
    --connection-name connectionName \
    --name flowName

```

##### Enable the given flow

```
az data-transfer connection flow enable \
    --resource-group groupName \
    --connection-name connectionName \
    --name flowName

```

##### Disable the given flow

```
az data-transfer connection flow disable \
    --resource-group groupName \
    --connection-name connectionName \
    --name flowName

```

##### Update the given flow

Update of the tags is only supported.

```
az data-transfer connection flow update \
    --resource-group groupName \
    --connection-name connectionName \
    --flow-name flowName \
    --tags key1=update1

```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.