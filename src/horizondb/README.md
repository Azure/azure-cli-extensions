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

To enable customer-managed data encryption, supply both `--primary-key-uri`
(a versionless Azure Key Vault key URI) and `--primary-user-assigned-identity-id`
(the managed identity resource ID, also available as `--primary-user-id` on
create, restore, and update). The command sends `dataEncryption.type` as
`AzureKeyVault`. Neither `--data-encryption` nor an encryption-type argument is
exposed. If neither encryption argument is supplied on create, encryption
configuration is omitted and the service uses system-managed encryption.

## Update cluster encryption

`az horizondb cluster update` exposes `--primary-key-uri` and
`--primary-user-assigned-identity-id` (alias `--primary-user-id`) instead of
`--data-encryption`. Either argument can be supplied independently. Only the
supplied encryption fields are sent in the PATCH request; omitted fields and the
existing encryption type remain unchanged. The service requires key URI and
identity changes to be completed in separate updates.

## Restore a cluster

Use the source cluster resource ID and an optional UTC restore time:

```powershell
az horizondb cluster restore --resource-group example-resource-group --cluster-name restored-cluster --source-cluster-id /subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/source-resource-group/providers/Microsoft.HorizonDb/clusters/source-cluster --point-in-time-utc 2026-07-27T12:00:00Z
```

Unspecified writable settings are inherited from the source cluster, including
location, tags, PostgreSQL version, geo-redundancy, network, encryption, identity, and
AI Model Management settings. Cluster-create options can override the inherited
settings they expose. To override source encryption, supply both
`--primary-key-uri` and `--primary-user-assigned-identity-id`; the command sets
the encryption type to `AzureKeyVault`. If neither is supplied, the source
encryption settings are inherited. Supplying only one is rejected.
The command sends
`creationMode` as `PointInTimeRestore`, waits for cluster provisioning, and
returns a final GET of the restored cluster. It does not create a pool.

`--point-in-time-utc` defaults to the current UTC time if not supplied. PostgreSQL
version and geo-redundancy are always inherited from the source cluster.
Backup retention days are not inherited or sent to the API during restore;
`--version`, `--geo-redundancy`, and `--retention-days` are not available
on restore. `--location` can only be specified for a geo-redundant restore when
the source cluster has geo-redundancy enabled. Otherwise, omit `--location` to
use the source cluster location.

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
