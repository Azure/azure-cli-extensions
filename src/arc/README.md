# Azure CLI Arc Extension #
This is an extension to manage Arc resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name arc
```

### Included Features ###
#### arc ####
##### Create #####
```
az arc gateway create --resource-group "myResourceGroup" --location "eastus2euap" --name "myGateway" --allowed-features *
```
##### List #####
```
az arc gateway list
```
##### Show #####
```
az arc gateway show --resource-group "myResourceGroup" --name "myGateway"
```
##### Update #####
```
az arc gateway update --resource-group "myResourceGroup" --name "myGateway"
```
##### Delete #####
```
az arc gateway delete --resource-group "myResourceGroup" --name "myGateway"
```