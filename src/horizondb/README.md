# Azure CLI HorizonDB Extension

This is the extension for Azure HorizonDB. It provides commands to manage HorizonDB clusters.

## How to use

Install this extension using the following CLI command:

```bash
az extension add --name horizondb
```

## Included Features

### HorizonDB Cluster Management

*Commands:*

- `az horizondb create`: Create a new Azure HorizonDB cluster.
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
