# Azure CLI DocumentDB Extension #

This is an extension to Azure CLI to manage **Azure DocumentDB**
clusters (the `Microsoft.DocumentDB/mongoClusters` resource) under the
`az documentdb mongocluster` command group.

Version `1.1.0b2` is a Beta release generated against the
`2026-06-15-preview` management API. The Preview API adds planned replica
promotion while retaining the existing command surface.

## How to install ##

```bash
az extension add --name documentdb
```

## Background ##

Azure DocumentDB is a fully managed, MongoDB-compatible database service.
This extension exposes the management-plane operations for mongo clusters and their
sub-resources: IP firewall rules, Microsoft Entra-backed database users, user-assigned
managed identity, cross-region read replicas, and point-in-time restore.

## Command groups ##

| Group | Description |
|--|--|
| `az documentdb mongocluster` | Create and manage mongo clusters |
| `az documentdb mongocluster firewall-rule` | Manage IP firewall rules (public access) |
| `az documentdb mongocluster microsoft-entra-user` | Manage Microsoft Entra ID database users |
| `az documentdb mongocluster identity` | Manage the cluster's user-assigned managed identity |
| `az documentdb mongocluster replica` | List, create, and promote cross-region read replicas |

## Usage examples ##

### Create and manage a cluster

```bash
# Create a cluster
az documentdb mongocluster create -n MyCluster -g MyResourceGroup --location eastus2 \
    --admin-user dbadmin --admin-password MyP@ssw0rd123! \
    --tier M30 --storage-size 128 --storage-type PremiumSSDv2 \
    --shard-count 1 --high-availability Disabled

# Show and list
az documentdb mongocluster show -n MyCluster -g MyResourceGroup
az documentdb mongocluster list -g MyResourceGroup

# Get connection strings
az documentdb mongocluster list-connection-strings -n MyCluster -g MyResourceGroup

# Reset the administrator password
az documentdb mongocluster reset-password -n MyCluster -g MyResourceGroup --password NewP@ssw0rd123!

# Delete
az documentdb mongocluster delete -n MyCluster -g MyResourceGroup
```

### Firewall rules

```bash
az documentdb mongocluster firewall-rule create -n AllowMyIp --cluster-name MyCluster \
    -g MyResourceGroup --start-ip-address 203.0.113.0 --end-ip-address 203.0.113.255
az documentdb mongocluster firewall-rule list --cluster-name MyCluster -g MyResourceGroup
```

### Microsoft Entra ID users

```bash
# The user is identified by its Microsoft Entra object (client) ID, not a friendly name.
az documentdb mongocluster microsoft-entra-user assign --object-id 11111111-1111-1111-1111-111111111111 \
    --cluster-name MyCluster -g MyResourceGroup --type User --role db=admin role=root
```

### Managed identity (user-assigned)

```bash
az documentdb mongocluster identity assign -n MyCluster -g MyResourceGroup \
    --mi-user-assigned <userAssignedIdentityResourceId>
az documentdb mongocluster identity show -n MyCluster -g MyResourceGroup
```

### Replicas (cross-region)

```bash
# List the source cluster's replicas
az documentdb mongocluster replica list --source-cluster MyCluster -g MyResourceGroup

# Create a cross-region GeoReplica (the source must have the GeoReplicas preview feature enabled).
# --source-cluster accepts the source cluster name or its full ARM resource ID; the source
# location is resolved automatically.
az documentdb mongocluster replica create -n MyReplica -g MyResourceGroup -l centralus \
    --source-cluster MyCluster

# Planned promotion waits for the replica to catch up before switching roles (Preview).
az documentdb mongocluster replica promote -n MyReplica -g MyResourceGroup \
    --source-cluster MyCluster --mode Switchover --promote-option Planned

# Forced promotion switches immediately and can lose recent writes; use it for recovery only.
az documentdb mongocluster replica promote -n MyReplica -g MyResourceGroup \
    --source-cluster MyCluster --mode Switchover --promote-option Forced
```

### Private Link

Private Link is managed through Azure CLI's core networking commands rather than a
dedicated `az documentdb mongocluster` subgroup:

| Operation | Command group |
| --- | --- |
| Create, inspect, or delete a private endpoint in a virtual network | `az network private-endpoint` |
| Discover the cluster's Private Link group ID and required DNS zones | `az network private-link-resource` |
| List, inspect, approve, reject, or delete service-side endpoint connections | `az network private-endpoint-connection` |

Use the cluster resource ID to discover its Private Link resources and list its
connections. For a restored cluster, use the restored cluster's name and resource group.

```bash
clusterId=$(az documentdb mongocluster show -n MyCluster -g MyResourceGroup --query id -o tsv)

az network private-link-resource list --id "$clusterId"
az network private-endpoint-connection list --id "$clusterId"
```

For connection-specific commands such as `show`, `approve`, `reject`, and `delete`,
pass the service-side connection ID returned by the connection list command to `--id`,
not the cluster ID or the network private endpoint ID.

The target subresource for endpoint creation is `MongoCluster`. Configure the virtual
network, subnet, and private DNS integration as described in the
[DocumentDB Private Link guide](https://learn.microsoft.com/azure/documentdb/how-to-private-link).
Use the required DNS zone names returned by the Private Link resource list for your environment.

Core networking commands select their own API versions. When an explicit DocumentDB
API version is required, use `az rest`, for example:

```bash
az rest --method get --url "${clusterId}/privateLinkResources?api-version=2026-06-15-preview"
az rest --method get --url "${clusterId}/privateEndpointConnections?api-version=2026-06-15-preview"
```

The restore option `--public-network-access Disabled` only disables public access; it
does not create a private endpoint, approve a connection, or configure private DNS.
Dedicated DocumentDB Private Link commands are a separate extension enhancement, not
part of the restore command.

### Point-in-time restore

The restore command supports the following optional target configuration settings:

| Setting | CLI parameter |
| --- | --- |
| Authentication modes | `--auth-allowed-modes` |
| Customer-managed key encryption | `--encryption` |
| User-assigned managed identities | `--user-assigned` |
| Storage type | `--storage-type` |
| Public network access | `--public-network-access` |
| Resource tags | `--tags` |

Overrides for server version, compute tier, storage size, shard count, high
availability, Data API, network bypass, and preview features are not supported by
this command. The restore-specific service schema rejects the `previewFeatures`
property, so preview features such as `GeoReplicas` cannot be specified as restore
overrides.

The existing native-authentication behavior remains the default. When
`--auth-allowed-modes` and `--encryption` are both omitted, both administrator
arguments are required.

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyCluster --restore-time "2026-06-30T10:00:00Z" \
    --admin-user dbadmin --admin-password MyP@ssw0rd123!
```

For Microsoft Entra-only authentication, omit the native administrator credentials.

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyEntraCluster --restore-time "2026-06-30T10:00:00Z" \
    --auth-allowed-modes MicrosoftEntraID
```

Customer-managed-key restore accepts the same user-assigned identity and encryption
shape as cluster creation. The identity referenced by the encryption configuration
must also be supplied through `--user-assigned`. CMK configures encryption, not
authentication. Supply administrator credentials when restoring with NativeAuth;
adding CMK does not remove that service requirement.

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyCluster --restore-time "2026-06-30T10:00:00Z" \
    --admin-user dbadmin --admin-password MyP@ssw0rd123! \
    --user-assigned <userAssignedIdentityResourceId> --encryption @encryption.json
```

Specify storage type and public network access with the corresponding options:

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyCluster --restore-time "2026-06-30T10:00:00Z" \
    --admin-user dbadmin --admin-password MyP@ssw0rd123! \
    --storage-type PremiumSSDv2 --public-network-access Disabled
```

Specify tags for the restored cluster with `--tags`. The supplied map sets the target
tags rather than merging with the source cluster's tags. Omitting this option leaves
the restore request unchanged.

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyCluster --restore-time "2026-06-30T10:00:00Z" \
    --admin-user dbadmin --admin-password MyP@ssw0rd123! \
    --tags environment=restored team=documentdb
```