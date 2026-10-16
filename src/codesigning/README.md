# Azure CLI codesigning Extension #
This is the extension for codesigning

### How to use ###
Install this extension using the below CLI command
```
az extension add --name codesigning
```

### Included Features ###
#### codesigning ####
##### Create #####
```
az codesigning create --name "MyAccount" --location "eastus" --resource-group "MyResourceGroup"
```
##### Show #####
```
az codesigning show --name "MyAccount" --resource-group "MyResourceGroup"
```
##### List #####
```
az codesigning list --resource-group "MyResourceGroup"
```
##### Update #####
```
az codesigning update --name "MyAccount" --tags key1="value1" --resource-group "MyResourceGroup"
```
##### Delete #####
```
az codesigning delete --name "MyAccount" --resource-group "MyResourceGroup"
```
#### codesigning certificate-profile ####
##### Create #####
```
az codesigning certificate-profile create --account-name "MyAccount" --common-name "Contoso Inc" \
    --organization "Contoso Inc" --name "profileA" --resource-group "MyResourceGroup" 
```
##### Show #####
```
az codesigning certificate-profile show --account-name "MyAccount" --name "profileA" --resource-group "MyResourceGroup"
```
##### List #####
```
az codesigning certificate-profile list --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### Delete #####
```
az codesigning certificate-profile delete --account-name "MyAccount" --name "profileA" \
    --resource-group "MyResourceGroup" 
```