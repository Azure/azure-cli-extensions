# Azure CLI healthbot Extension #
This is the extension for healthbot

### How to use ###
Install this extension using the below CLI command
```
az extension add --name healthbot
```

### Included Features ###
#### healthbot bot ####
##### Create #####
```
az healthbot bot create --name "samplebotname" --location "East US" --sku name="F0" --resource-group "healthbotClient"
```
##### Show #####
```
az healthbot bot show --name "samplebotname" --resource-group "healthbotClient"
```
##### List #####
```
az healthbot bot list --resource-group "OneResourceGroupName"
```
##### Update #####
```
az healthbot bot update --name "samplebotname" --sku name="F0" --resource-group "healthbotClient"
```
##### Delete #####
```
az healthbot bot delete --name "samplebotname" --resource-group "healthbotClient"
```