# Azure CLI HorizonDB Extension

This is the extension for Azure HorizonDB. It provides commands to manage HorizonDB clusters.

## How to use

Install this extension using the following CLI command:

```bash
az extension add --name horizondb
```

## Local development

From the repository root, activate your development virtual environment and
install this extension from source:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install azdev
azdev setup -r "$PWD" -e horizondb
```

Confirm that the extension path points to this checkout and try the generated
pool command group:

```powershell
az extension show --name horizondb
az horizondb cluster pool --help
```

Local source edits take effect on the next command invocation. The generated
pool commands are under `horizondb cluster pool`, not `horizondb pool`.

## Create a cluster

`az horizondb cluster create` creates the cluster and polls every 30 seconds for
up to one hour until its provisioning state is `Succeeded`. It does not create
a default pool or accept pool compute and availability arguments:

```powershell
az horizondb cluster create --resource-group example-resource-group --cluster-name example-cluster --location eastus2 --version 17 --geo-redundancy Enabled
```

The command returns the provisioned cluster. If cluster provisioning fails or
times out, the command reports the error. Create pools separately using
`az horizondb cluster pool create`.

## Included Features

### HorizonDB Cluster Management

*Commands:*

- `az horizondb create`: Create a new Azure HorizonDB cluster.
- `az horizondb restore`: Restore an Azure HorizonDB cluster from a source cluster.
- `az horizondb delete`: Delete an Azure HorizonDB cluster.
- `az horizondb show`: Show details of an Azure HorizonDB cluster.

### HorizonDB Private Endpoint Connections

*Commands:*

- `az horizondb private-endpoint-connection list`: List private endpoint connections for a HorizonDB cluster.
- `az horizondb private-endpoint-connection show`: Show details of a HorizonDB private endpoint connection.
- `az horizondb private-endpoint-connection approve`: Approve a HorizonDB private endpoint connection.
- `az horizondb private-endpoint-connection reject`: Reject a HorizonDB private endpoint connection.
- `az horizondb private-endpoint-connection delete`: Delete a HorizonDB private endpoint connection.

### HorizonDB Private Link Resources

*Commands:*

- `az horizondb private-link-resource list`: List private link resources for a HorizonDB cluster.
- `az horizondb private-link-resource show`: Show details of a HorizonDB private link resource.
