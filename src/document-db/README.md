# Azure CLI DocumentDb Extension
This is an extension to Azure CLI to manage Document DB resources.

This includes:
- Create/update Mongo cluster instances.
- Add/remove firewall rules to a cluster.
- Restoring cluster to a point in time from backups.
- Promoting a replica cluster to be a primary cluster.

## How to use

Install the extension with this command:

```bash
az extension add --name document-db
```

Use help `-h` to get a list of available commands:
```bash
az document-db cluster -h
```

And to get a description of a command and usage examples:
```bash
az document-db cluster <command> -h
```

### Create a new Mongo cluster

```bash
az document-db cluster create --resource-group TestResourceGroup --cluster-name myMongoCluster \
    --location westus2 --administrator-name mongoAdmin --administrator-password password231 \
    --server-version 5.0 --storage-size-gb 128 --compute-tier M30 \
    --shard-count 1 --high-availability-mode ZoneRedundantPreferred
```

### Create a replica cluster
```bash
az document-db cluster replica create --resource-group TestResourceGroup \
    --cluster-name myMongoCluster --location eastus2 --source-location westus3 \
    --source-resource mySourceMongoCluster
```

### Promote a replica cluster
```bash
az document-db cluster replica promote --resource-group TestGroup \
    --cluster-name replicaMongoCluster --promote-option Forced \
    --promote-mode Switchover
```