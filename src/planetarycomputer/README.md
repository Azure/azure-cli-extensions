# Azure CLI Planetary Computer Extension #
This is an extension to Azure CLI to manage Planetary Computer GeoCatalog resources.

## How to use ##

### Install the extension ###
```bash
az extension add --name planetarycomputer
```

### Commands ###

#### GeoCatalog Management ####
```bash
# Create a GeoCatalog
az planetarycomputer geocatalog create -g MyResourceGroup -n MyCatalog -l eastus

# Show a GeoCatalog
az planetarycomputer geocatalog show -g MyResourceGroup -n MyCatalog

# List GeoCatalogs in a resource group
az planetarycomputer geocatalog list -g MyResourceGroup

# List all GeoCatalogs in a subscription
az planetarycomputer geocatalog list

# Update tags on a GeoCatalog
az planetarycomputer geocatalog update -g MyResourceGroup -n MyCatalog --tags env=prod

# Delete a GeoCatalog
az planetarycomputer geocatalog delete -g MyResourceGroup -n MyCatalog

# Wait for a GeoCatalog to reach a desired state
az planetarycomputer geocatalog wait -g MyResourceGroup -n MyCatalog --created
```

#### GeoCatalog Identity Management ####
```bash
# Assign a user-assigned managed identity
az planetarycomputer geocatalog identity assign -g MyResourceGroup -n MyCatalog --user-assigned /subscriptions/<subscription-id>/resourceGroups/MyResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity

# Show identity information
az planetarycomputer geocatalog identity show -g MyResourceGroup -n MyCatalog

# Remove a user-assigned managed identity
az planetarycomputer geocatalog identity remove -g MyResourceGroup -n MyCatalog --user-assigned /subscriptions/<subscription-id>/resourceGroups/MyResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity
```