# Azure CLI Agent Mesh Extension

This extension manages Azure Agent Mesh fabrics, fabric members, and policy groups.
It uses the `Microsoft.NetworkSecurity` resource provider API version
`2026-07-21-preview`.

## Install

```bash
az extension add --name agentmesh
```

## Commands

Each resource supports `create`, `show`, `list`, `update`, and `delete`.

```bash
az agentmesh fabric --help
az agentmesh fabric member --help
az agentmesh policy-group --help
```

### Fabrics

```bash
az agentmesh fabric create \
  --resource-group myResourceGroup \
  --name myFabric \
  --location eastus \
  --trust-domain contoso.agentfabric

az agentmesh fabric update \
  --resource-group myResourceGroup \
  --name myFabric \
  --tags environment=production

az agentmesh fabric list --resource-group myResourceGroup
```

### Fabric members

```bash
az agentmesh fabric member create \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --member-name myMember \
  --location eastus \
  --workload resourceId=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ContainerInstance/containerGroups/myContainerGroup

az agentmesh fabric member show \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --member-name myMember
```

### Policy groups

```bash
az agentmesh policy-group create \
  --resource-group myResourceGroup \
  --name myPolicyGroup \
  --location eastus \
  --display-name "My policy group" \
  --priority 100

az agentmesh policy-group list --resource-group myResourceGroup
```

Long-running create, update, and delete operations support `--no-wait`. Use the
corresponding `wait` command to wait for provisioning to reach a target state.