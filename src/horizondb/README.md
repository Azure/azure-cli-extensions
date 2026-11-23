# Azure CLI HorizonDB Extension

Manage Azure HorizonDB clusters, compute pools, pool firewall rules, parameter
groups, and private endpoint connections.

This extension is in **preview** and requires **Azure CLI 2.75.0 or later**.

## Install and sign in

```powershell
az login
az account set --subscription "<subscription-id>"
az extension add --name horizondb --allow-preview true
```

Use `az horizondb --help` to explore the command groups, or append `--help`
to a command to see its options.

The examples below use placeholder resource names and `eastus2`. Replace these
with your own values and a location where HorizonDB is available to your subscription.

## Create a cluster and a pool

A cluster does not automatically create a compute pool. Create the cluster first,
then create its pool:

```powershell
az group create --name example-resource-group --location eastus2
az horizondb cluster create --resource-group example-resource-group --name example-cluster --location eastus2 --version 17 --geo-redundancy Disabled --public-access Disabled
az horizondb cluster pool create --resource-group example-resource-group --cluster-name example-cluster --name example-pool --compute-processor AMD --compute-generation 3 --v-cores 2 --node-count 1 --high-availability-mode Disabled
```

Cluster creation supports PostgreSQL major versions `17` and `18`. The version
cannot be changed through an in-place cluster update.

Public access is disabled by default. Choose either private connectivity or
explicitly enable public access and configure pool firewall rules as described below.

Cluster create and restore wait for provisioning and return the resulting cluster.
Use `--no-wait` to return after submitting the request instead. To check a cluster
created with `--no-wait`, use `az horizondb cluster show` or
`az horizondb cluster wait --created` with its resource group and name.

Backup retention defaults to 7 days. Set `--backup-retention-days` to a value
from 1 through 35; `--retention-days` remains an alias on create.

Compute and high-availability settings belong to the pool, not the cluster.
A single-node pool requires `--high-availability-mode Disabled`; pools with
multiple nodes require `AnyZone` or `ZoneRedundant`.

For example, scale the pool's vCores:

```powershell
az horizondb cluster pool update --resource-group example-resource-group --cluster-name example-cluster --name example-pool --v-cores 4
```

## Manage parameter groups

Create a parameter group for the cluster's PostgreSQL version, then associate
it with an existing pool. Pools use the default parameter group when created;
custom parameter groups are assigned through pool update.

```powershell
az horizondb parameter-group create --resource-group example-resource-group --name example-parameters --location eastus2 --version 17 --parameters "[{name:work_mem,value:8192}]"
$parameterGroupId = az horizondb parameter-group show --resource-group example-resource-group --name example-parameters --query id --output tsv
az horizondb cluster pool update --resource-group example-resource-group --cluster-name example-cluster --name example-pool --param-group-id $parameterGroupId --param-group-apply Immediate
```

`--param-group-apply` accepts `Immediate` or `PendingReboot`. Static parameter
changes still require a pool restart, regardless of the apply method.
Use `az horizondb parameter-group connection list` with `--resource-group` and
`--parameter-group-name` to inspect the group's connections.

## Restore a cluster

Restore to a new cluster using the source cluster's resource ID:

```powershell
$sourceClusterId = az horizondb cluster show --resource-group example-resource-group --name example-cluster --query id --output tsv
az horizondb cluster restore --resource-group example-resource-group --name restored-cluster --source-cluster-id $sourceClusterId
```

`--point-in-time-utc` is optional and defaults to five minutes before the current
UTC time. To choose another time, supply a UTC timestamp such as
`YYYY-MM-DDTHH:MM:SSZ` within the source's available backup history.

The restored cluster inherits the source's PostgreSQL version and geo-redundancy.
It also inherits location, tags, network, encryption, identity, and AI Model
Management settings unless an exposed restore option overrides them.

`--version`, `--geo-redundancy`, and backup-retention options are not available
on restore. Backup retention is not copied into the restore request.
Only specify `--location` when the source has geo-redundancy enabled; otherwise,
omit it to use the source location. Restore does not create a pool.

## Customer-managed encryption keys

On cluster create or restore, supply both `--primary-key-uri` and
`--primary-user-assigned-identity-id` (alias `--primary-user-id`). The key URI
must be versionless, for example `https://example.vault.azure.net/keys/example-key`.
Ensure the identity has the required Key Vault key permissions before using it.

The command enables Azure Key Vault encryption and assigns the selected identity
to the cluster. Restore preserves the source's existing identity assignments and
adds the selected encryption identity. These assignments do not grant Key Vault
permissions.

Creation without either argument uses system-managed encryption; restore without
either argument inherits source encryption. Supplying only one on create or
restore is rejected. Geo-redundant backup is not supported with customer-managed
encryption, so use `--geo-redundancy Disabled` when creating a CMK-encrypted cluster.

For an existing CMK-encrypted cluster, rotate the key with a separate update:

```powershell
az horizondb cluster update --resource-group example-resource-group --name example-cluster --primary-key-uri https://example.vault.azure.net/keys/new-key
```

Only supplied encryption fields are updated. To change the encryption identity,
use `--primary-user-assigned-identity-id`; the identity must already be assigned
to the cluster because update does not add identity assignments. Complete a key
change before submitting an identity change, or vice versa.

## Private connectivity

Discover the cluster's private link resources:

```powershell
az horizondb cluster private-link-resource list --resource-group example-resource-group --cluster-name example-cluster
```

Use the returned group ID when creating the consumer-side endpoint with
`az network private-endpoint create` in your virtual network and subnet.
Then list the cluster's connections and use the returned connection name
(which can differ from the network private endpoint's name):

```powershell
az horizondb cluster private-endpoint-connection list --resource-group example-resource-group --cluster-name example-cluster
az horizondb cluster private-endpoint-connection update --resource-group example-resource-group --cluster-name example-cluster --name example-connection --status Approved --description "Connection approved"
```

Approval requires the cluster to contain at least one pool. To reject a connection,
use the same update command with `--status Rejected`:

```powershell
az horizondb cluster private-endpoint-connection update --resource-group example-resource-group --cluster-name example-cluster --name example-connection --status Rejected --description "Connection rejected"
```

Private endpoint connection show/update output is flattened: query `privateEndpoint.id` and
`privateLinkServiceConnectionState.status`, not `properties.privateEndpoint.id`
or `properties.privateLinkServiceConnectionState.status`.

## Public access and pool firewall rules

For public connectivity, enable cluster public access and add a pool firewall
rule restricted to your client IP. Replace the documentation-only address below
with your actual client IPv4 address:

```powershell
az horizondb cluster update --resource-group example-resource-group --name example-cluster --public-access Enabled
az horizondb cluster pool firewall-rule create --resource-group example-resource-group --cluster-name example-cluster --pool-name example-pool --name client-access --start-ip-address 203.0.113.10 --end-ip-address 203.0.113.10
```

## Included Features

### HorizonDB Cluster Management

*Commands:*

- `az horizondb cluster create`: Create a HorizonDB cluster.
- `az horizondb cluster restore`: Restore a HorizonDB cluster from a source cluster.
- `az horizondb cluster delete`: Delete a HorizonDB cluster.
- `az horizondb cluster list`: List HorizonDB clusters.
- `az horizondb cluster show`: Show details of a HorizonDB cluster.
- `az horizondb cluster update`: Update a HorizonDB cluster.
- `az horizondb cluster wait`: Wait for a cluster to satisfy a condition.

### HorizonDB Pool Management

*Commands:*

- `az horizondb cluster pool create`: Create a pool in a HorizonDB cluster.
- `az horizondb cluster pool delete`: Delete a pool.
- `az horizondb cluster pool list`: List pools in a cluster.
- `az horizondb cluster pool show`: Show details of a pool.
- `az horizondb cluster pool update`: Update a pool.
- `az horizondb cluster pool wait`: Wait for a pool to satisfy a condition.

### HorizonDB Pool Firewall Rules

*Commands:*

- `az horizondb cluster pool firewall-rule create`: Create a pool firewall rule.
- `az horizondb cluster pool firewall-rule delete`: Delete a pool firewall rule.
- `az horizondb cluster pool firewall-rule list`: List firewall rules for a pool.
- `az horizondb cluster pool firewall-rule show`: Show details of a pool firewall rule.
- `az horizondb cluster pool firewall-rule update`: Update a pool firewall rule.
- `az horizondb cluster pool firewall-rule wait`: Wait for a firewall rule to satisfy a condition.

### HorizonDB Private Endpoint Connections

*Commands:*

- `az horizondb cluster private-endpoint-connection list`: List private endpoint connections for a cluster.
- `az horizondb cluster private-endpoint-connection show`: Show details of a private endpoint connection.
- `az horizondb cluster private-endpoint-connection update`: Approve, reject, or update an existing connection.
- `az horizondb cluster private-endpoint-connection delete`: Delete a private endpoint connection.
- `az horizondb cluster private-endpoint-connection wait`: Wait for a connection to satisfy a condition.

### HorizonDB Private Link Resources

*Commands:*

- `az horizondb cluster private-link-resource list`: List private link resources for a cluster.
- `az horizondb cluster private-link-resource show`: Show details of a private link resource.

### HorizonDB Parameter Groups

*Commands:*

- `az horizondb parameter-group create`: Create a parameter group.
- `az horizondb parameter-group delete`: Delete a parameter group.
- `az horizondb parameter-group list`: List parameter groups.
- `az horizondb parameter-group show`: Show details of a parameter group.
- `az horizondb parameter-group update`: Update a parameter group.
- `az horizondb parameter-group wait`: Wait for a parameter group to satisfy a condition.
- `az horizondb parameter-group connection list`: List connections associated with a parameter group.

## Local development

For contributors, run the following from the repository root to use a source
checkout instead of the published extension:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install azdev
azdev setup -r "$PWD" -e horizondb
az horizondb cluster pool --help
```
