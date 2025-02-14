# Azure CLI Datafactory Extension #
This is a extension for datafactory features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name datafactory
```

### Included Features
#### Factory:
Manage a data factory: [more info](https://docs.microsoft.com/en-us/azure/data-factory/introduction)  
*Examples:*
```
az datafactory factory create \
    --location location \
    --name factoryName \
    --resource-group groupName

az datafactory factory update \
    --name factoryName\
    --tags exampleTag="exampleValue" \
    --resource-group groupName
```

#### LinkedService:
Managed a linked service associated with the factory: [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-linked-services)  
*Examples:*  
```
az datafactory linked-service create \
    --factory-name factoryName \
    --properties @{propertiesJsonPath} \
    --name linkedServiceName \
    --resource-group groupName
```

#### Dataset
Managed a view of the data that you want to use in data factory: [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-datasets-linked-services)  
*Examples:*  
```
az datafactory dataset create \
    --properties @{propertiesJsonPath}
    --name datasetName \
    --factory-name factoryName \
    --resource-group groupName
```

#### Pipeline
Use pipeline to define a set of activities to operate on your dataset: [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipelines-activities)  
*Examples:*  
```
az datafactory pipeline create \
    --factory-name factoryName \
    --pipeline @{pipelineJsonPath} \
    --name pipelineName \
    --resource-group groupName

az datafactory pipeline update \
    --factory-name factoryName \
    --activities @{activitiesJsonPath} \
    --parameters @{parametersJsonPath} \
    --run-dimensions @{runDimensionJsonPath} \
    --variables @{variableJsonPath}
    --name pipelineName \
    --resource-group groupName
```

#### Pipeline-Run
You can manually execute your pipeline activities(on demand): [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipeline-execution-triggers#manual-execution-on-demand)  
*Examples:*  
```
az datafactory pipeline create-run \
    --factory-name factoryName \
    --parameters @{parametersJsonPath} \ # parameters pass to the pipeline activities
    --name pipelineName \
    --resource-group groupName
```
In the create run step, you will get a pipeline runId. Now you can choose to cancel this execution  
```
az datafactory pipeline-run cancel \
    --factory-name factoryName \
    --resource-group groupName \
    --run-id runId
```
You can query the pipeline run by factory 
```
az datafactory pipeline-run query-by-factory \
    --factory-name factoryName \
    --filters filterCondition \ # example: 
operand="PipelineName" operator="Equals" values="myPipeline" 
    --last-updated-after queryStartTime \
    --last-updated-before queryEndTime \
    --resource-group groupName
```
You can also query the activities run by pipeline runId
```
az datafactory activity-run query-by-pipeline-run \
    --factory-name factoryName \
    --last-updated-after queryStartTime \
    --last-updated-before queryEndTime \
    --resource-group groupName \
    --run-id runId
```

#### Trigger
Triggers are the other way that you can execute a pipeline run: [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipeline-execution-triggers#trigger-execution)  
*Examples:*  
```
az datafactory trigger create \
    --factory-name factoryName \
    --resource-group groupName \
    --properties @{propertiesJsonPath} \
    --name triggerName

# start a trigger
az datafactory trigger start \
    --factory-name factoryName \
    --resource-group groupName \
    --name triggerName

# stop a trigger
az datafactory trigger stop \
    --factory-name factoryName \
    --resource-group groupName \
    --name triggerName
```

You can use the query trigger run and rerun a trigger run if needed.  
```
az datafactory trigger-run query-by-factory \
    --factory-name factoryName \
    --filters filterCondition \
    --last-updated-after queryStartTime \
    --last-updated-before queryEndTime \
    --resource-group groupName

# You will get a triggerRunId for each trigger run. If it's not in process status, you can rerun it. Please note that the rerun can only apply to Tumble Window Trigger.
az datafactory trigger-run rerun \
    --factory-name factoryName \
    --resource-group groupName \
    --run-id triggerRunId \
    --trigger-name triggerName
```

#### Integration-Runtime
The Integration-Runtime (IR) is the compute infrastructure used by data factory to provide the data integration capabilities: [more info](https://docs.microsoft.com/en-us/azure/data-factory/concepts-integration-runtime)  
*Examples:*  
```
az datafactory integration-runtime self-hosted create \
    --factory-name factoryName \
    --description description \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime managed create \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName \
    --description description \
    --type-properties-compute-properties @{computePropertiesJsonPath} \
    --type-properties-ssis-properties @{ssisPropertiesJsonPath} 

az datafactory integration-runtime update \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName \
    --auto-update updateMode \
    --update-delay-offset delayOffset
```
If it's a self-hosted IR, you need to go to the portal to create the integration runtime nodes, but you can perform the following operations on it.  
```
az datafactory integration-runtime get-connection-info \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime get-status \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime list-auth-key \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime regenerate-auth-key \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --key-name keyName \
    --resource-group groupName

az datafactory integration-runtime sync-credentials \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime upgrade \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime-node get-ip-address  \
    --factory-name factoryName \
    --integration-runtime-name integrationRuntimeName \
    --node-name nodeName \
    --resource-group groupName
```
If it's a managed IR, you can perform the following operations on it
```
az datafactory integration-runtime start \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName

az datafactory integration-runtime stop \
    --factory-name factoryName \
    --name integrationRuntimeName \
    --resource-group groupName
```