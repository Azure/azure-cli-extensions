# Azure CLI Interconnect Extension #
This is an extension to Azure CLI to manage Interconnect resources.

## How to use ##
Install the extension:

```
az extension add --name interconnect
```

### Manage interconnect groups ###

Create an interconnect group:

```
az interconnect-group create --resource-group rg1 --interconnect-group-name test-ig
```

Show an interconnect group:

```
az interconnect-group show --resource-group rg1 --interconnect-group-name test-ig
```

List interconnect groups (in a subscription, or scoped to a resource group):

```
az interconnect-group list
az interconnect-group list --resource-group rg1
```

Update an interconnect group:

```
az interconnect-group update --resource-group rg1 --interconnect-group-name test-ig
```

Delete an interconnect group:

```
az interconnect-group delete --resource-group rg1 --interconnect-group-name test-ig
```

Get node availability for all subgroups in an interconnect group:

```
az interconnect-group get-node-availability --resource-group rg1 --interconnect-group-name test-ig
```

### Manage subgroups ###

List subgroups in an interconnect group:

```
az interconnect-group subgroup list --resource-group rg1 --interconnect-group-name test-ig
```

Show a subgroup:

```
az interconnect-group subgroup show --resource-group rg1 --interconnect-group-name test-ig --subgroup-name subgroup0
```
