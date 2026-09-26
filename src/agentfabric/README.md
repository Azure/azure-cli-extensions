# Azure CLI Agent Fabric Extension

This extension manages Azure Agent Fabric resources, AKS cluster enrollment,
child members, and independent Policy Group peer resources. It uses the
`Microsoft.NetworkSecurity` resource provider API version
`2026-07-21-preview`, with AKS enrollment using `2026-09-10-preview`.

## Resource hierarchy

```text
Microsoft.NetworkSecurity
├── agentFabrics/{fabricName} (independent top-level resource)
│   ├── members/{memberName} (child of an Agent Fabric)
│   └── clusterAssociations/{clusterName} (AKS enrollment implementation resource)
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

## AKS enrollment

Create the Agent Fabric separately, then use `az agentfabric aks` to attach
AKS managed clusters. The cluster must be in the same subscription as the
Agent Fabric, but it can be in a different resource group. The AKS cluster name
is used as the underlying Cluster Association child resource name, while the
cluster resource ID is immutable.

```bash
az agentfabric aks attach \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --cluster-name myCluster \
  --cluster-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myAksResourceGroup/providers/Microsoft.ContainerService/managedClusters/myCluster \
  --sku Standard

az agentfabric aks show \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --cluster-name myCluster
```

Supported SKUs are `Standard` and `Premium`. Run `aks attach` once per AKS
cluster to enroll multiple clusters in the same Agent Fabric. Use `aks update`
to change an enrollment SKU and `aks detach` to remove an enrollment.

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

Long-running create, attach, update, detach, and delete operations support
`--no-wait`. Use the corresponding `wait` command to wait for provisioning to
reach a target state.
