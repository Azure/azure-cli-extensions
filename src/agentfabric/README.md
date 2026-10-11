# Azure CLI Agent Fabric Extension

This extension manages Azure Agent Fabric resources, AKS cluster enrollment,
child members, and independent Policy Group peer resources. It uses the
`Microsoft.NetworkSecurity` resource provider API version
`2026-10-07-preview`.

The commands are generated from the public contract on `RPSaaSDev` at commit
`01be2263f53dd57906029e65115a9e475624be74` in
[Azure/azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr/tree/01be2263f53dd57906029e65115a9e475624be74/specification/networksecurity/resource-manager/Microsoft.NetworkSecurity/agentFabric/preview/2026-10-07-preview).
This pins the API contract, not the version deployed in an Azure region.

## Resource hierarchy

```text
Microsoft.NetworkSecurity
├── agentFabrics/{fabricName} (independent top-level resource)
│   ├── members/{memberName} (child of an Agent Fabric)
│   ├── clusterAssociations/{associationName} (compute enrollment implementation resource)
│   └── egressTrustBundles/default (read-only certificate bundle)
└── policyGroups/{policyGroupName} (independent top-level peer resource)
```

## Install

```bash
az extension add --name agentfabric
```

## Agent Fabrics

Root CRUD commands manage Agent Fabric resources.

Fabrics support a system-assigned managed identity and a customer-owned Content
Safety connection. The connection is configured using the Fabric PUT operation
(`create`, which can also replace an existing fabric), not the tags/identity
PATCH operation (`update`). A nonempty connection requires both endpoint and
API key, including when rotating a key at the same endpoint. The API key is
write-only and is not returned by show or list.

Omitting the connection or supplying an empty object preserves an existing
connection. For a new fabric, either form requests no inspection connection.
The service does not create a Content Safety account or fall back to shared
credentials for a newly configured customer-owned connection.

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

Workloads support `ACI`, `AKS`, and `AgentFabricSandbox` variants. AKS workloads
include the association ID, AKS resource ID, and an existing Kubernetes resource
reference; the CLI does not create that Kubernetes resource. Endpoint mappings
use `name`, `service-port`, `protocol`, and `target-port`, replacing the earlier
single `port` field. Member PATCH supports tags and `fqdn`, not workload changes.

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
Agent Fabric, but it can be in a different resource group. `--association-name`
identifies the enrollment child, independently of the target cluster name.
`--name/-n` and the earlier `--cluster-name` are aliases for that child name;
they do not resolve the target cluster ID. The target resource ID is immutable.
The latest wire contract also allows ACI SandboxGroup target IDs.

```bash
az agentfabric aks attach \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --association-name myEnrollment \
  --location eastus \
  --cluster-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myAksResourceGroup/providers/Microsoft.ContainerService/managedClusters/myCluster \
  --sku Standard

az agentfabric aks show \
  --resource-group myResourceGroup \
  --fabric-name myFabric \
  --association-name myEnrollment
```

Supported SKUs are `Standard` and `Premium`. Run `aks attach` once per AKS
cluster to enroll multiple clusters in the same Agent Fabric. Use `aks update`
to change an enrollment SKU and `aks detach` to remove an enrollment.

The latest API supports Standard-to-Premium upgrades, but rejects a downgrade
from Premium to Standard. Cluster Associations are now tracked resources with
location and tags. This differs from the earlier proxy-resource contract.
`aks update` first reads the enrollment to obtain its immutable target ID,
then PATCHes tags, SKU, or `--workload-cluster-gateway-ip`. Users do not need to
resupply the target ID. `aks wait` observes ARM provisioning state, not
Kubernetes readiness. Attach does not currently send `If-None-Match`; it uses
the API's create-or-replace PUT semantics rather than a create-only guarantee.

## Egress trust bundles

Egress trust bundles expose the certificate material and cache lifetime for a
Fabric's egress trust configuration. The API supports only show and list; the
item endpoint is the singleton `egressTrustBundles/default`. These are
read-only operations and do not install certificates on a cluster.

```bash
az agentfabric egress-trust-bundle show \
  --resource-group myResourceGroup \
  --fabric-name myFabric

az agentfabric egress-trust-bundle list \
  --resource-group myResourceGroup \
  --fabric-name myFabric
```

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
