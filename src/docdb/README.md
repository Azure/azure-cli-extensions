# Azure CLI Database for Document DB Extension
This is an extension to Azure CLI to manage Database for Document DB resources.

This includes:
- Create/update cluster instances.
- Add/remove firewall rules to a cluster.
- Restoring cluster to a point in time from backups.
- Promoting a replica cluster to be a primary cluster.

## How to use

Install the extension with this command:

```bash
az extension add --name docdb
```

Use help `-h` to get a list of available commands:
```bash
az docdb cluster -h
```

And to get a description of a command and usage examples:
```bash
az docdb cluster <command> -h
```

### Create a new cluster

```bash
az docdb cluster create --resource-group TestResourceGroup --cluster-name myCluster \
    --location westus2 --administrator-name myAdmin --administrator-password password231 \
    --server-version 5.0 --storage-size-gb 128 --compute-tier M30 \
    --shard-count 1 --high-availability-mode ZoneRedundantPreferred
```

### Create a replica cluster
```bash
az docdb cluster replica create --resource-group TestResourceGroup \
    --cluster-name myCluster --location eastus2 --source-location westus3 \
    --source-resource mySourceCluster
```

### Promote a replica cluster
```bash
az docdb cluster replica promote --resource-group TestGroup \
    --cluster-name replicaCluster --promote-option Forced \
    --promote-mode Switchover
```