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
    --diagnostics-path "waimportexport" --export blob-path-prefix="/" --job-type "Export" --log-level "Verbose" \
    --return-address city="Redmond" country-or-region="USA" email="Test@contoso.com" phone="4250000000" postal-code="98007" recipient-name="Test" state-or-province="wa" street-address1="Street1" street-address2="street2" \
    --return-shipping carrier-account-number="989ffff" carrier-name="FedEx" \
    --storage-account-id "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.ClassicStorage/storageAccounts/test" \
    --name "myExportJob" --resource-group "myResourceGroup" 
```
##### Create #####
```
az storageimportexport job create --location "West US" --backup-drive-manifest true \
    --diagnostics-path "waimportexport" \
    --drive-list bit-locker-key="238810-662376-448998-450120-652806-203390-606320-483076" drive-header-hash="0:1048576:FB6B6ED500D49DA6E0D723C98D42C657F2881CC13357C28DCECA6A524F1292501571A321238540E621AB5BD9C9A32637615919A75593E6CB5C1515DAE341CABF;135266304:143360:C957A189AFC38C4E80731252301EB91427CE55E61448FA3C73C6FDDE70ABBC197947EC8D0249A2C639BB10B95957D5820A4BE8DFBBF76FFFA688AE5CE0D42EC3" drive-id="9CA995BB" manifest-file="\\\\8a0c23f7-14b7-470a-9633-fcd46590a1bc.manifest" manifest-hash="4228EC5D8E048CB9B515338C789314BE8D0B2FDBC7C7A0308E1C826242CDE74E" \
    --job-type "Import" --log-level "Verbose" \
    --return-address city="Redmond" country-or-region="USA" email="Test@contoso.com" phone="4250000000" postal-code="98007" recipient-name="Test" state-or-province="wa" street-address1="Street1" street-address2="street2" \
    --return-shipping carrier-account-number="989ffff" carrier-name="FedEx" \
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
##### Show #####
```
az storageimportexport job show --name "myJob" --resource-group "myResourceGroup"
```
##### Update #####
```
az storageimportexport job update --backup-drive-manifest true --log-level "Verbose" --state "" --name "myExportJob" \
    --resource-group "myResourceGroup" 
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