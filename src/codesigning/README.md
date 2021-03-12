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
az codesigning create --account-name "MyAccount" --location "eastus" --resource-group "MyResourceGroup"
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
az codesigning update --tags key1="value1" --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### Delete #####
```
az codesigning delete --account-name "MyAccount" --resource-group "MyResourceGroup"
```
#### codesigning certificate-profile ####
##### Create #####
```
az codesigning certificate-profile create --account-name "MyAccount" --profile-name "profileA" --common-name "Contoso" \
    --profile-type "PublicTrust" --subject-alternative-name "Contoso Corporate Engineering" \
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
##### Update #####
```
az codesigning certificate-profile update --common-name "Contoso" --profile-type "Test" \
    --subject-alternative-name "Contoso Corporate Engineering" --account-name "MyAccount" --profile-name "profileA" \
    --resource-group "MyResourceGroup" 
```
##### Delete #####
```
az codesigning certificate-profile delete --account-name "MyAccount" --profile-name "profileA" \
    --resource-group "MyResourceGroup" 
```
#### codesigning operation ####
##### Show #####
```
az codesigning operation show
```