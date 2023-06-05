# Azure CLI Extension for Microsoft Dev Box and Azure Deployment Environments #
This is the Azure CLI extension for [Microsoft Dev Box](https://learn.microsoft.com/azure/dev-box/) and [Azure Deployment Environments](https://learn.microsoft.com/azure/deployment-environments/)

### How to use ###
Install this extension using the below CLI command
``` sh
az extension add --name devcenter
```

### Usage ###
See [Microsoft Dev Box and Azure Deployment Environments Azure CLI reference](https://learn.microsoft.com/cli/azure/devcenter?view=azure-cli-latest)
 
#### devcenter admin ####
Manage admin resources with devcenter
``` sh
az devcenter admin
```
#### devcenter dev ####
Manage developer resources with devcenter
``` sh
az devcenter dev
```

### Update ###
Update this extension using the below CLI command
``` sh
az extension update --name devcenter
```
### Uninstall ###
Run `az extension list` to see if the extension is installed.

Run `az --version` to see the current verion of the extension. 

To remove the extension use the below CLI command
``` sh
az extension remove --name devcenter
```