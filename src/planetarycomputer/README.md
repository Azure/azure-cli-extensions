# Azure CLI Planetary Computer Extension #
This is an extension to Azure CLI to manage Planetary Computer GeoCatalog resources.

The extension targets `Microsoft.Orbital` API version `2026-10-01`.

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

#### GeoCatalog Network Access ####
```bash
# Disable public network access
az planetarycomputer geocatalog update -g MyResourceGroup -n MyCatalog --public-network-access Disabled

# List private endpoint connections
az planetarycomputer geocatalog private-endpoint-connection list -g MyResourceGroup --catalog-name MyCatalog

# Show a private endpoint connection
az planetarycomputer geocatalog private-endpoint-connection show -g MyResourceGroup --catalog-name MyCatalog -n MyConnection

# List private link resources
az planetarycomputer geocatalog private-link-resource list -g MyResourceGroup --catalog-name MyCatalog
```

GeoCatalog creation also supports `--tier Premium` with
`--premium-configuration`. Use
`az planetarycomputer geocatalog create --help` for the configuration fields.

## Development smoke test ##

From the repository root in the configured `azdev` environment:

```bash
python -m unittest discover -s src/planetarycomputer/azext_planetarycomputer/tests/latest -p test_stable_api.py -v
```

This offline smoke test invokes the CLI with mocked HTTP responses; it does not
validate the live service. The existing scenario recordings still target
`2026-04-15` and need refreshing before the full playback suite and pre-push gate
can pass.