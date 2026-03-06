# Azure CLI AppnetPreview Extension #
This is an extension to Azure CLI to manage Application Network resources.

## How to use ##

### Install the extension
```bash
az extension add --name appnet-preview
```

### List available Application Network versions
```bash
az appnet list-versions --location <location>
```

### Create an Application Network
```bash
az appnet create --resource-group <resource-group> --appnet-name <name> --location <location>
```

### Join an AKS cluster to an Application Network

**Prerequisites:** You must have an existing AKS cluster before running `az appnet member join`.

```bash
# Create an AKS cluster first (if you don't have one)
az aks create --resource-group <resource-group> --name <aks-name> --location <location>

# Get the AKS cluster resource ID
AKS_ID=$(az aks show --resource-group <resource-group> --name <aks-name> --query id -o tsv)

# Join the AKS cluster to the Application Network
az appnet member join --resource-group <resource-group> --appnet-name <appnet-name> \
    --member-name <member-name> --cluster-type AKS --member-resource-id $AKS_ID \
    --upgrade-mode FullyManaged --release-channel Stable
```

### Other commands
```bash
# List Application Networks
az appnet list --resource-group <resource-group>

# Show an Application Network
az appnet show --resource-group <resource-group> --name <appnet-name>

# List members in an Application Network
az appnet member list --resource-group <resource-group> --appnet-name <appnet-name>

# Remove a member from an Application Network
az appnet member remove --resource-group <resource-group> --appnet-name <appnet-name> --member-name <member-name>

# Delete an Application Network
az appnet delete --resource-group <resource-group> --name <appnet-name>
```
