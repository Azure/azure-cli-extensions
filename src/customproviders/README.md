# Azure CLI customproviders Extension #
This is the extension for customproviders

### How to use ###
Install this extension using the below CLI command
```
az extension add --name customproviders
```

### Included Features ###
#### customproviders custom-resource-provider ####
##### Create #####
```
az customproviders custom-resource-provider create --resource-group "testRG" --location "eastus" \
    --actions name="TestAction" endpoint="https://mytestendpoint/" routing-type="Proxy" \
    --resource-types name="TestResource" endpoint="https://mytestendpoint2/" routing-type="Proxy,Cache" \
    --resource-provider-name "newrp" 
```
##### Show #####
```
az customproviders custom-resource-provider show --resource-group "testRG" --resource-provider-name "newrp"
```
##### List #####
```
az customproviders custom-resource-provider list --resource-group "testRG"
```
##### Update #####
```
az customproviders custom-resource-provider update --resource-group "testRG" --resource-provider-name "newrp"
```
##### Delete #####
```
az customproviders custom-resource-provider delete --resource-group "testRG" --resource-provider-name "newrp"
```
#### customproviders association ####
##### Create #####
```
az customproviders association create \
    --target-resource-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/appRG/providers/Microsoft.Solutions/applications/applicationName" \
    --name "associationName" --scope "scope" 

az customproviders association wait --created --name "{myAssociation}"
```
##### Show #####
```
az customproviders association show --name "associationName" --scope "scope"
```
##### List-all #####
```
az customproviders association list-all --scope "scope"
```
##### Delete #####
```
az customproviders association delete --name "associationName" --scope "scope"
```