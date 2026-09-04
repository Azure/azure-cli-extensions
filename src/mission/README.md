# Azure CLI Mission Extension #
This is an extension to Azure CLI to manage Azure Virtual Enclaves (Microsoft.Mission) resources.

## How to use ##
Install this extension using the below CLI command:
```
az extension add --name mission
```

Then use the `az mission` command group, for example:
```
az mission community list --resource-group MyRg
az mission community show --resource-group MyRg --community-name MyCommunity
az mission virtual-enclave list --resource-group MyRg
```

Run `az mission --help` (or `az mission community create --help`) to see the full list of command groups, commands, and their parameters.