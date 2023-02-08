# Azure CLI for Mcirosoft Dev Box and Azure Deployment Environments Extension #
This is the extension for [Microsoft Dev Box](https://learn.microsoft.com/azure/dev-box/) and [Azure Deployment Environments](https://learn.microsoft.com/azure/deployment-environments/)

### How to use ###
Install this extension using the below CLI command
``` sh
az extension add --name devcenter
```

### Usage ###
See the [Microsoft Dev Box Preview Azure CLI reference](https://learn.microsoft.com/azure/dev-box/cli-reference-subset) and the [Azure Deployment Environments Azure CLI reference](https://learn.microsoft.com/azure/deployment-environments/how-to-configure-use-cli).
 
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

### Uninstall ###
You can see if the extension is installed by running `az extension list`.
You can see the current version of your extension by running `az --version`.
You can remove the extension by running:
``` sh
az extension remove --name vmware
```