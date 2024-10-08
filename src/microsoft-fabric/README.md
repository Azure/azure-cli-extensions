# Azure CLI Microsoft Fabric Extension #
This is an extension to Azure CLI to manage Microsoft Fabric resources.

## How to use ##

Install the latest version of the extension:

```cli
az extension add --name microsoft-fabric
```

Validate that the extension is installed correctly:

```cli
az fabric --help
```

For list of available versions, see [the extension release history](https://github.com/Azure/azure-cli-extensions/blob/main/src/microsoft-fabric/HISTORY.rst).

To install a specific version of the fabric CLI extension, add `--version` parameter to the command. For example, below installs 1.0.0

```cli
az extension add --name microsoft-fabric --version 1.0.0
```

## Included Features ##

Below is a high-level overview of microsoft fabric commands.

### Microsoft Fabric Capacity Management ##

| Commands                                       | Description                                                           |
|------------------------------------------------|-----------------------------------------------------------------------|
| az fabric capacity create                      | Create a FabricCapacity.                                              |
| az fabric capacity delete                      | Delete a FabricCapacity.                                              |
| az fabric capacity show                        | Get a FabricCapacity.                                                 | 
| az fabric capacity update                      | Update a FabricCapacity.                                              |
| az fabric capacity list                        | List FabricCapacity resources by subscription ID.                     |
| az fabric capacity suspend                     | Suspend operation of the specified Fabric capacity instance.          |
| az fabric capacity resume                      | Resume operation of the specified Fabric capacity instance.racks.     |
| az fabric capacity list-skus                   | List eligible SKUs for Microsoft Fabric resource provider.            |
| az fabric capacity list-skus-for-capacity      | List eligible SKUs for a Microsoft Fabric resource.                   |
| az fabric capacity check-name-availability     | Implements local CheckNameAvailability operations.                    |
