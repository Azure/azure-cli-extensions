# Azure ManagedOps CLI guide

Use the `managedops` Azure CLI extension to configure the subscription-scoped
Azure ManagedOps instance.

> [!IMPORTANT]
> ManagedOps is a subscription singleton. Its resource name must be `default`,
> and only one instance can exist in a subscription.

## Prerequisites

1. Sign in and select the target subscription:

   ```azurecli
   az login
   az account set --subscription "<subscription-name-or-id>"
   ```

1. Install or update the extension:

   ```azurecli
   az extension add --name managedops --upgrade
   ```

1. Prepare these existing Azure resources:

   - Azure Monitor workspace
   - Log Analytics workspace
   - User-assigned managed identity

The examples below use these placeholders:

```text
<azure-monitor-workspace-resource-id>
<log-analytics-workspace-resource-id>
<user-assigned-managed-identity-resource-id>
```

The multiline examples use Bash and Azure Cloud Shell line continuations. In
PowerShell, replace each trailing backslash (`\`) with a backtick (`` ` ``).

You can retrieve the resource IDs with:

```azurecli
az monitor account show \
  --resource-group "<resource-group>" \
  --name "<azure-monitor-workspace>" \
  --query id --output tsv

az monitor log-analytics workspace show \
  --resource-group "<resource-group>" \
  --workspace-name "<log-analytics-workspace>" \
  --query id --output tsv

az identity show \
  --resource-group "<resource-group>" \
  --name "<managed-identity>" \
  --query id --output tsv
```

## Command summary

| Command | Purpose |
| --- | --- |
| `az managedops managedops create` | Create or configure the `default` ManagedOps instance. |
| `az managedops managedops show` | Display the current ManagedOps configuration and status. |
| `az managedops managedops update` | Update Defender CSPM or Defender for Servers enablement. |
| `az managedops managedops wait` | Wait for creation, update, deletion, or a custom condition. |
| `az managedops managedops delete` | Delete the ManagedOps instance. |

## Create ManagedOps

```azurecli
az managedops managedops create \
  --name default \
  --sku "{name:ManagedOps,tier:Essential}" \
  --amw-id "<azure-monitor-workspace-resource-id>" \
  --law-id "<log-analytics-workspace-resource-id>" \
  --uami-id "<user-assigned-managed-identity-resource-id>" \
  --defender-cspm Disable \
  --defender-for-servers Disable
```

The Defender options accept `Enable` or `Disable` and default to `Disable`.

> [!IMPORTANT]
> The Azure Monitor workspace, Log Analytics workspace, and managed identity
> resource IDs cannot be changed after the ManagedOps instance is created.

## Show ManagedOps

Show the complete resource:

```azurecli
az managedops managedops show --name default
```

Show a concise status summary:

```azurecli
az managedops managedops show \
  --name default \
  --query "{state:properties.provisioningState,cspm:properties.desiredConfiguration.defenderCspm,servers:properties.desiredConfiguration.defenderForServers}" \
  --output table
```

## Update Defender settings

```azurecli
az managedops managedops update \
  --name default \
  --defender-cspm Enable \
  --defender-for-servers Enable
```

> [!WARNING]
> After Defender CSPM or Defender for Servers has been successfully enabled,
> the service does not allow it to be disabled on the same ManagedOps instance.

## Run commands asynchronously

Add `--no-wait` to `create`, `update`, or `delete` to return immediately:

```azurecli
az managedops managedops update \
  --name default \
  --defender-cspm Enable \
  --no-wait
```

Then wait for the operation:

```azurecli
az managedops managedops wait --name default --updated
```

Other wait conditions include:

```azurecli
az managedops managedops wait --name default --created
az managedops managedops wait --name default --exists
az managedops managedops wait --name default --deleted
```

The default polling interval is 30 seconds and the default timeout is 3600
seconds. Override them with `--interval` and `--timeout`.

## Delete ManagedOps

Delete with an interactive confirmation:

```azurecli
az managedops managedops delete --name default
```

Delete without prompting:

```azurecli
az managedops managedops delete --name default --yes
```

Delete asynchronously and wait for completion:

```azurecli
az managedops managedops delete --name default --yes --no-wait
az managedops managedops wait --name default --deleted
```

## Get command help

```azurecli
az managedops managedops --help
az managedops managedops create --help
az managedops managedops update --help
```
