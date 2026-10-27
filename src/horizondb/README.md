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

## Create a cluster with a default pool

`az horizondb cluster create` creates the cluster and polls every 30 seconds for
up to one hour until its provisioning state is `Succeeded`. Only then does it
create a child pool named `defaultpool` and wait for pool provisioning to finish.
Progress messages indicate when the command is waiting for the cluster and when
it starts creating the default pool. All five compute and availability arguments
are required:

```powershell
az horizondb cluster create --resource-group example-resource-group --cluster-name example-cluster --location eastus2 --version 17 --geo-redundancy Enabled --compute-processor AMD --compute-generation 3 --v-cores 2 --node-count 1 --high-availability-mode Disabled
```

For one node, high availability must be `Disabled`. For two through sixteen
nodes, use `AnyZone` or `ZoneRedundant`. The pool request does not include a
parameter group. The command returns the cluster after both requests succeed.
If cluster provisioning fails or times out, the command reports the error and
does not create the pool. If pool creation fails, the command reports the error
and leaves the cluster in place; it does not roll back cluster creation.

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
