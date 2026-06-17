# Azure CLI health-models Extension #
This is the extension for Azure Health Models.
Azure Health Models (`Microsoft.CloudHealth`) represent the operational health of a workload as an entity graph. Entities are services or components, edges are parent-child relationships, and each entity carries health signals derived from metrics or logs. Signals roll up through the graph. Alerts can be configured to get notified on health changes.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name health-models
```

### Included Features ###
#### monitor health-models ####
##### Create #####
```
az monitor health-models create --name "myModel" --resource-group "myRG" --location "eastus"
```
##### Show #####
```
az monitor health-models show --name "myModel" --resource-group "myRG"
```
##### List #####
```
az monitor health-models list --resource-group "myRG"
```
##### Update #####
```
az monitor health-models update --name "myModel" --resource-group "myRG" --tags env=prod
```
##### Delete #####
```
az monitor health-models delete --name "myModel" --resource-group "myRG"
```
#### Sub-resources ####
The model is composed of `entity`, `signal-definition`, `relationship`, `authentication-setting`, and `discovery-rule` collections, plus `identity` for managed-identity assignment. Each follows the same `create / show / list / update / delete` pattern.

E.g. to create an entity and a signal definition:

```
az monitor health-models entity create --health-model-name "myModel" --resource-group "myRG" --name "frontend" --display-name "Frontend"
az monitor health-models signal-definition create --health-model-name "myModel" --resource-group "myRG" --name "cpuPressure" --display-name "CPU Pressure" --refresh-interval PT5M --azure-resource-metric '{...}'
```
