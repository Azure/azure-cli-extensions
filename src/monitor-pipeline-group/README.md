# Azure CLI monitor-pipeline-group Extension #
This is an extension to Azure CLI to manage Azure Monitor Pipeline Group (Microsoft.Monitor/pipelineGroups) resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name monitor-pipeline-group
```

### Included Features
#### pipeline-group
##### Create
```
az monitor pipeline-group create --resource-group "myResourceGroup" --location "eastus" --name "myPipeline" --exporters @exporters.json --processors @processors.json --receivers @receivers.json --service @service.json --network-config [] --replicas 1 --extended-location @extendedLocation.json
```
##### Show
```
az monitor pipeline-group show --resource-group "myResourceGroup" --name "myPipeline"
```
##### List
```
az monitor pipeline-group list --resource-group "myResourceGroup"
```
##### Update
```
az monitor pipeline-group update --resource-group "myResourceGroup" --name "myPipeline" --service @service.json --exporters @exporters.json --processors @processors.json --receivers @receivers.json --service @service.json
```
##### Delete
```
az monitor pipeline-group delete --resource-group "myResourceGroup" --name "myPipeline"
```