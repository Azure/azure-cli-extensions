# Azure CLI storageimportexport Extension #
This is the extension for storageimportexport

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storageimportexport
```

### Included Features ###
#### storageimportexport location ####
##### List #####
```
az storageimportexport location list
```
##### Show #####
```
az storageimportexport location show --name "West US"
```
#### storageimportexport job ####
##### Create #####
```
az storageimportexport job create --location "West US" --backup-drive-manifest true \
    --diagnostics-path "waimportexport" \
    --drive-list bit-locker-key="238810-662376-448998-450120-652806-203390-606320-483076" drive-header-hash="" drive-id="9CA995BB" manifest-file="\\\\DriveManifest.xml" manifest-hash="109B21108597EF36D5785F08303F3638" \
    --job-type "Import" --log-level "Verbose" \
    --return-address city="Redmond" country-or-region="USA" email="Test@contoso.com" phone="4250000000" postal-code="98007" recipient-name="Tets" state-or-province="wa" street-address1="Street1" street-address2="street2" \
    --storage-account-id "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.ClassicStorage/storageAccounts/test" \
    --name "myJob" --resource-group "myResourceGroup" 
```
##### Show #####
```
az storageimportexport job show --name "myJob" --resource-group "myResourceGroup"
```
##### List #####
```
az storageimportexport job list --resource-group "myResourceGroup"
```
##### Update #####
```
az storageimportexport job update --backup-drive-manifest true --log-level "Verbose" --state "" --name "myJob" \
    --resource-group "myResourceGroup" 
```
##### Delete #####
```
az storageimportexport job delete --name "myJob" --resource-group "myResourceGroup"
```
#### storageimportexport bit-locker-key ####
##### List #####
```
az storageimportexport bit-locker-key list --job-name "myJob" --resource-group "myResourceGroup"
```