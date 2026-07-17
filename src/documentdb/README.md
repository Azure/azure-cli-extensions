# Azure CLI DocumentDB Extension #

This is an extension to Azure CLI to manage **Azure Cosmos DB for MongoDB (vCore)**
clusters — the `Microsoft.DocumentDB/mongoClusters` resource — under the
`az documentdb mongocluster` command group.

## How to install ##

```bash
az extension add --name documentdb
```

## Background ##

DocumentDB (Mongo vCore) is a fully managed, MongoDB-compatible database service.
This extension exposes the management-plane operations for mongo clusters and their
sub-resources: IP firewall rules, Microsoft Entra-backed database users, user-assigned
managed identity, cross-region read replicas, and point-in-time restore.

## Command groups ##

| Group | Description |
|--|--|
| `az documentdb mongocluster` | Create and manage mongo clusters |
| `az documentdb mongocluster firewall-rule` | Manage IP firewall rules (public access) |
| `az documentdb mongocluster entra-user` | Manage Microsoft Entra ID database users |
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
az documentdb mongocluster entra-user create --object-id 11111111-1111-1111-1111-111111111111 \
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
# List the parent cluster's replicas
az documentdb mongocluster replica list --cluster-name MyCluster -g MyResourceGroup

# Create a cross-region GeoReplica (the source must have the GeoReplicas preview feature enabled)
az documentdb mongocluster replica create -n MyReplica -g MyResourceGroup -l centralus \
    --source-cluster MyCluster --source-location eastus2

# Promote a replica to primary
az documentdb mongocluster replica promote -n MyReplica -g MyResourceGroup
```

### Point-in-time restore

```bash
az documentdb mongocluster restore -n RestoredCluster -g MyResourceGroup --location eastus2 \
    --source-cluster MyCluster --restore-time "2026-06-30T10:00:00Z" \
    --admin-user dbadmin --admin-password MyP@ssw0rd123!
```