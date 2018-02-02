# Azure CLI Enhanced Monitoring Extension #
This is an extension to azure cli which provides commands to configure, verify and remove Azure Enhanced Monitoring Extension for SAP 

## How to use ##
First, install the extension:
```
az extension add --name aem
```

Then, call it as you would any other az command:
```
az vm aem set --resource-group rg --name vm1
```