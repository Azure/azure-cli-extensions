# Azure CLI Edge Action Extension

Manage Azure Front Door Edge Actions, code versions, execution filters, and route
attachments with Azure CLI.

This extension uses the stable `2026-10-01` API. Version 1.0.0 is its first stable release. It requires
Azure CLI 2.75.0 or later.

## Installation

```bash
az extension add --name edge-action
```

To update an existing installation:

```bash
az extension update --name edge-action
```

Use `az edge-action --help` or append `--help` to a command for its available options.

## Commands

### Edge Action management

```bash
# Create an edge action
az edge-action create --resource-group myResourceGroup --name myEdgeAction --location global --sku name=Standard tier=Standard

# List edge actions in a resource group
az edge-action list --resource-group myResourceGroup

# Show edge action details
az edge-action show --resource-group myResourceGroup --name myEdgeAction

# Update edge action
az edge-action update --resource-group myResourceGroup --name myEdgeAction --tags env=prod

# Delete an edge action
az edge-action delete --resource-group myResourceGroup --name myEdgeAction
```

### Version management

```bash
# Create a version
az edge-action version create --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1 --location global --deployment-type file --is-default-version True

# Deploy JavaScript code to a version
az edge-action version deploy-from-file --resource-group myResourceGroup --edge-action-name myEdgeAction --version v1 --file-path ./mycode.js

# List versions
az edge-action version list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Download version code as a ZIP file
az edge-action version get-version-code --resource-group myResourceGroup --edge-action-name myEdgeAction --version v1 --output-directory ./downloads

# Delete a version
az edge-action version delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1
```

When no default version exists, the service makes the new version default even
if `--is-default-version False` is supplied. If a default version already exists,
create additional versions with `--is-default-version False`; `True` is rejected.
Use `swap-default`, not `version update`, to change the default to another existing version:

```bash
az edge-action version swap-default --resource-group myResourceGroup --edge-action-name myEdgeAction --version v2
```

`get-version-code --output-directory` (alias `-d`) creates the directory if needed
and saves `<response-name>.zip`, overwriting an existing file with that name.
It returns `file` and `message` fields. Without this option, it returns `name` and
base64-encoded `content`. With `--no-wait`, it does not wait for or save the download.
Invalid download content and file-write errors are reported.

### Execution filters

Replace the resource ID placeholders below with an existing version's resource ID.

```bash
# Create an execution filter
az edge-action execution-filter create --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --location global --version-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/edgeActions/{name}/versions/{version} --execution-filter-identifier-header-name x-edge-action --execution-filter-identifier-header-value enabled

# List execution filters
az edge-action execution-filter list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Update one execution-filter field; omitted fields are preserved
az edge-action execution-filter update --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --execution-filter-identifier-header-value updated

# Point the filter to another version under the same Edge Action
az edge-action execution-filter update --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --version-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/edgeActions/{name}/versions/v2

# Delete an execution filter
az edge-action execution-filter delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter
```

Execution-filter `update` supports `--tags`, `--version-id`,
`--execution-filter-identifier-header-name`, and
`--execution-filter-identifier-header-value`, independently or together.
Omitted fields are preserved. Tags replace the tag collection; use `--tags "{}"`
to clear it. The header name/value pair must be unique among filters under the
same Edge Action; multiple filters can reference the same version.

Generic updates run after named arguments and take precedence on the same field.
For example, use `--set execution_filter_identifier_header_value=enabled` or
`--remove tags.purpose`, not `properties.executionFilterIdentifierHeaderValue`.
Generic options remain subject to the resource schema and service validation;
`--add` requires a list property, and this resource has no writable list properties.

## Features

- Full lifecycle management of Azure Front Door Edge Actions
- Version control for Edge Action code
- JavaScript and zip file deployment support
- Execution filter management for selective Edge Action execution


## Development

See the [developer guide](https://github.com/Azure/azure-cli-extensions/blob/main/src/edge-action/DEVELOPMENT.md)
for command generation, customizations, testing, and recording guidance.
