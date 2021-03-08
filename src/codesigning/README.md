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
az codesigning create --account-name "MyAccount" --location "eastus" --tags key1="value1" \
    --resource-group "MyResourceGroup" 
```
##### Show #####
```
az codesigning show --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### List #####
```
az codesigning list --resource-group "MyResourceGroup"
```
##### Update #####
```
az codesigning update --account-name "MyAccount" --tags key1="value1" --resource-group "MyResourceGroup"
```
##### Delete #####
```
az codesigning delete --account-name "MyAccount" --resource-group "MyResourceGroup"
```
#### codesigning certificate-profile ####
##### Create #####
```
az codesigning certificate-profile create --account-name "MyAccount" --profile-name "profileA" \
    --resource-group "MyResourceGroup" 
```
##### Show #####
```
az codesigning certificate-profile show --account-name "MyAccount" --profile-name "profileA" \
    --resource-group "MyResourceGroup" 
```
##### List #####
```
az codesigning certificate-profile list --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### Delete #####
```
az codesigning certificate-profile delete --account-name "MyAccount" --profile-name "profileA" \
    --resource-group "MyResourceGroup" 
```
#### codesigning operation ####