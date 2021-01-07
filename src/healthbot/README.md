# Azure CLI healthbot Extension #
This is the extension for healthbot

### How to use ###
Install this extension using the below CLI command
```
az extension add --name healthbot
```

### Included Features ###
#### healthbot ####
##### Create #####
```
az healthbot create --bot-name "samplebotname" --location "East US" --name "F0" --resource-group "healthbotClient"
```
##### Show #####
```
az healthbot show --name "samplebotname" --resource-group "healthbotClient"
```
##### List #####
```
az healthbot list --resource-group "OneResourceGroupName"
```
##### Update #####
```
az healthbot update --bot-name "samplebotname" --name "F0" --resource-group "healthbotClient"
```
##### Delete #####
```
az healthbot delete --name "samplebotname" --resource-group "healthbotClient"
```