# Azure CLI Edge Action Extension

Azure CLI extension for managing Azure Front Door (AFD) Edge Actions.

## Overview

Edge Actions allow you to customize how Azure Front Door handles requests and responses at the edge. This extension provides commands to create, manage, and deploy Edge Actions for Azure Front Door.

## Installation

```bash
az extension add --name edge-action
```

## Commands

### Edge Action Management

```bash
# Create an edge action
az edge-action create --resource-group myResourceGroup --name myEdgeAction --location global --sku name=Standard tier=Standard

# List edge actions
az edge-action list --resource-group myResourceGroup

# Show edge action details
az edge-action show --resource-group myResourceGroup --name myEdgeAction

# Update edge action
az edge-action update --resource-group myResourceGroup --name myEdgeAction --tags env=prod

# Delete edge action
az edge-action delete --resource-group myResourceGroup --name myEdgeAction
```

### Version Management

```bash
# Create a version
az edge-action version create --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1 --location global --deployment-type file

# Deploy code to a version
az edge-action version deploy-from-file --resource-group myResourceGroup --edge-action-name myEdgeAction --version v1 --file-path ./mycode.js

# List versions
az edge-action version list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Delete a version
az edge-action version delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1
```

### Execution Filters

```bash
# Create an execution filter
az edge-action execution-filter create --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --location global --action-version-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/edgeActions/{name}/versions/{version}

# List execution filters
az edge-action execution-filter list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Delete an execution filter
az edge-action execution-filter delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter
```

## Features

- Full lifecycle management of Azure Front Door Edge Actions
- Version control for Edge Action code
- JavaScript and zip file deployment support
- Execution filter management for selective Edge Action execution
- Azure Front Door route attachment support
