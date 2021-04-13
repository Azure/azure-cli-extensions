# Azure CLI dfp Extension #
This is the extension for dfp

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dfp
```

### Included Features ###
#### dfp instance ####
##### Create #####
```
az dfp instance create --name "azsdktest" --location "West US" \
    --administration members="azsdktest@microsoft.com" members="azsdktest2@microsoft.com" --tags testKey="testValue" \
    --resource-group "TestRG" 

az dfp instance wait --created --name "{myInstance}" --resource-group "{rg}"
```
##### List #####
```
az dfp instance list --resource-group "TestRG"
```
##### Update #####
```
az dfp instance update --name "azsdktest" \
    --administration members="azsdktest@microsoft.com" members="azsdktest2@microsoft.com" --tags testKey="testValue" \
    --resource-group "TestRG" 
```
##### Show-detail #####
```
az dfp instance show-detail --name "azsdktest" --resource-group "TestRG"
```
##### Delete #####
```
az dfp instance delete --name "azsdktest" --resource-group "TestRG"
```
#### dfp ####
##### List-operation #####
```
az dfp list-operation
```