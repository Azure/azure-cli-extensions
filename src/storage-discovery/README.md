# Azure CLI StorageDiscovery Extension #
This is an extension to Azure CLI to manage StorageDiscovery resources.

## How to use ##
### az storage-discovery workspace create ###
```commandline
az storage-discovery workspace create \
  --resource-group myRG \
  --name myWorkspace \
  --location francecentral \
  --workspace-roots "/subscriptions/mySubId/resourceGroups/myRG" \
  --scopes '[{"displayName":"basic","resourceTypes":["Microsoft.Storage/storageAccounts"]}]'
```

### az storage-discovery workspace create (with full configuration) ###
```commandline
az storage-discovery workspace create \
  --resource-group myRG \
  --name myWorkspace \
  --location francecentral \
  --description "My workspace for storage discovery" \
  --sku Standard \
  --workspace-roots "/subscriptions/mySubId/resourceGroups/myRG" \
  --scopes '[{"displayName":"production","resourceTypes":["Microsoft.Storage/storageAccounts"],"tagKeysOnly":["environment"],"tags":{"project":"demo","tier":"prod"}}]'
```

### az storage-discovery workspace show ###
```commandline
az storage-discovery workspace show --resource-group myRG --name myWorkspace
```

### az storage-discovery workspace update ###
```commandline
az storage-discovery workspace update \
  --resource-group myRG \
  --name myWorkspace \
  --description "Updated description" \
  --sku Free \
  --scopes '[{"displayName":"updated","resourceTypes":["Microsoft.Storage/storageAccounts"],"tags":{"environment":"test"}}]' \
  --tags environment=production team=storage
```

```commandline
az storage-discovery workspace update \
  --resource-group myRG \
  --name myWorkspace \
  --capabilities "{azure-blob-storage:{capacity-details:{status:Disabled}}}"
```

### az storage-discovery workspace list ###
```commandline
az storage-discovery workspace list --resource-group myRG
```

### az storage-discovery workspace list (subscription level) ###
```commandline
az storage-discovery workspace list
```

### az storage-discovery workspace delete ###
```commandline
az storage-discovery workspace delete --resource-group myRG --name myWorkspace
```

## Workspace queries and reports (Preview)

These commands use API version `2026-10-01-preview`.

### az storage-discovery workspace query

Execute queries directly against a workspace without specifying a named report.
Replace `<base64-encoded-query-payload>` with your encoded query payload, following
the format described by `--queries` in command help. See the
[Storage Discovery query documentation](https://aka.ms/storageDiscoveryQuery)
for query syntax and available tables.

```commandline
az storage-discovery workspace query \
  --resource-group myRG \
  --storage-discovery-workspace-name myWorkspace \
  --queries "<base64-encoded-query-payload>"
```

### az storage-discovery workspace report list

List named report resources for a workspace in a specific resource group:

```commandline
az storage-discovery workspace report list \
  --resource-group myRG \
  --storage-discovery-workspace-name myWorkspace
```

Omit `--resource-group` to use the subscription-scoped list operation. The
workspace name is still required:

```commandline
az storage-discovery workspace report list \
  --storage-discovery-workspace-name myWorkspace
```

### az storage-discovery workspace report show

Retrieve an existing named report resource:

```commandline
az storage-discovery workspace report show \
  --resource-group myRG \
  --storage-discovery-workspace-name myWorkspace \
  --name myReport
```

### az storage-discovery workspace report generate-report

Execute report generation against an existing named report. Unlike `workspace
query`, this operation requires both the workspace name and the report name.
Use a valid report name from `workspace report list`; these commands do not
provide a report-create operation.

```commandline
az storage-discovery workspace report generate-report \
  --resource-group myRG \
  --storage-discovery-workspace-name myWorkspace \
  --discovery-resource-name myReport \
  --queries "<base64-encoded-query-payload>"
```

Both `workspace query` and `workspace report generate-report` wait for the
operation to complete and return its results. Neither command exposes `--no-wait`.