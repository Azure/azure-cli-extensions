# Azure CLI arcgateway Extension #
This is the extension for arcgateway

### How to use ###
Install this extension using the below CLI command
```
az extension add --name arcgateway
```

### Included Features ###
#### arcgateway ####
##### Create #####
```
az arcgateway create --name MyArcgateway --resource-group myResourceGroup --location eastus2euap --subscription mySubscription --allowed-features *
```
##### List #####
```
az arcgateway list --subscription mySubscription
```
##### Show #####
```
az arcgateway show --name myArcgateway --resource-group myResourceGroup --subscription mySubscription
```
##### Update #####
```
az arcgateway update --name MyArcgateway --resource-group myResourceGroup --subscription mySubscription
```
##### Delete #####
```
az arcgateway delete --name MyArcgateway --resource-group myResourceGroup --subscription mySubscription
```
#### arcgateway settings ####
##### Update #####
```
az arcgateway settings update --resource-group myResourceGroup --subscription mySubscription --base-provider Microsoft.HybridCompute --base-resource-type machines --base-resource-name workloadServer --settings-resource-name default --gateway-resource-id myResourceId