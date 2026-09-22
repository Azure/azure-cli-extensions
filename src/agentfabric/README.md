# Azure CLI Agent Fabric Extension

This extension manages Azure Agent Fabric resources, their child members and
cluster associations, and independent Policy Group peer resources. It uses the
`Microsoft.NetworkSecurity` resource provider API version
`2026-07-21-preview`, with Cluster Associations using
`2026-09-10-preview`.

## Resource hierarchy

```text
Microsoft.NetworkSecurity
├── agentFabrics/{fabricName} (independent top-level resource)
│   ├── members/{memberName} (child of an Agent Fabric)
│   └── clusterAssociations/{clusterAssociationName} (child of an Agent Fabric)
└── policyGroups/{policyGroupName} (independent top-level peer resource)
```

## Install

```bash
az extension add --name agentfabric
```

## Agent Fabrics

Root CRUD commands manage Agent Fabric resources.

```bash
az agentfabric create \
  --resource-group myResourceGroup \
  --name myFabric \
  --location eastus \
  --trust-domain contoso.agentfabric

az agentfabric update \
  --resource-group myResourceGroup \
  --name myFabric \
  --tags environment=production

az agentfabric list --resource-group myResourceGroup
```

## Members

Members are children of an Agent Fabric, so member commands require the parent
Fabric name through `--fabric-name`.

```bash
az agentfabric member create \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --member-name myMember \
  --location eastus \
  --workload "{aci:{resource-id:/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ContainerInstance/containerGroups/myContainerGroup}}"

az agentfabric member show \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --member-name myMember
```

## Cluster Associations

Cluster Associations enroll AKS managed clusters with an Agent Fabric. The
cluster must be in the same subscription as the Agent Fabric, but it can be in
a different resource group. The cluster resource ID is immutable; delete and
recreate the association to enroll a different cluster.

```bash
az agentfabric cluster-association create \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --name myClusterAssociation \
  --cluster-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myAksResourceGroup/providers/Microsoft.ContainerService/managedClusters/myCluster \
  --sku Standard \
  --if-none-match '*'

az agentfabric cluster-association show \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --name myClusterAssociation
```

Supported SKUs are `Standard` and `Premium`.

## Policy Groups

Policy Groups are independent resource-group-scoped
`Microsoft.NetworkSecurity` peer resources. They are not children of an Agent
Fabric, and their commands do not accept `--fabric-name`.

```bash
az agentfabric policy-group create \
  --resource-group myResourceGroup \
  --name myPolicyGroup \
  --location eastus \
  --display-name "My policy group" \
  --priority 100

az agentfabric policy-group show \
  --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.NetworkSecurity/policyGroups/myPolicyGroup
```

Policy Group ARM IDs end with `/policyGroups/{name}`.

Long-running create, update, and delete operations support `--no-wait`. Use
the corresponding `wait` command to wait for provisioning to reach a target
state.
