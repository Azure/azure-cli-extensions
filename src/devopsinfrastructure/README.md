# Azure CLI DevOpsInfrastructure Extension #
This is an extension to Azure CLI to manage [DevOpsInfrastructure resources](https://aka.ms/mdp-docs).

### How to use ###
Install this extension using the below CLI command
``` sh
az extension add --name dev-ops-infrastructure
```

### Usage ###
See [Managed DevOps Pools](https://learn.microsoft.com/cli/azure/devopsinfrastructure?view=azure-cli-latest)
 
#### devcenter pool ####
Manage resources with Managed DevOps Pools/
``` sh
az dev-ops-infrastructure pool
```

### Update ###
Update this extension using the below CLI command
``` sh
az extension update --name dev-ops-infrastructure
```
### Uninstall ###
Run `az extension list` to see if the extension is installed.

Run `az --version` to see the current verion of the extension. 

To remove the extension use the below CLI command
``` sh
az extension remove --name dev-ops-infrastructure
```