# Azure CLI ResourceMover Extension #
This package is for the 'resource-mover' extension, i.e. 'az resource-mover'. More info on what is [Azure Resource Mover](https://docs.microsoft.com/en-us/azure/resource-mover/overview).

## How to use
Install this extension using the below CLI command
```
az extension add --name resource-mover
```

## Included Features
### Manage move-collection

Create a move-collection with system assigned identity.
```
az resource-mover move-collection create \
    --identity type=SystemAssigned \
    --location eastus2 \
    --source-region eastus \
    --target-region westus \
    --name MyMoveCollection \
    --resource-group MyResourceGroup
```

Update the created move-collection.
```
az resource-mover move-collection update \
    --identity type=SystemAssigned \
    --tags key1=value1 \
    --name MyMoveCollection \
    --resource-group MyResourceGroup
```

Show information about a move-collection.
```
az resource-mover move-collection show \
    --name MyMoveCollection \
    --resource-group MyResourceGroup
```

Delete a move-collection.
```
az resource-mover move-collection delete \
    --name MyMoveCollection \
    --resource-group MyResourceGroup
```

#### Manage move-resource

Add a vNet as a move-resource to the move-collection.
```
az resource-mover move-resource add \
    --resource-group MyResourceGroup \
    --move-collection-name MyMoveCollection \
    --name MoveResourceName \
    --source-id "/subscriptions/subID/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/MyVNet" \
    --resource-settings '{ \
            "resourceType": "Microsoft.Network/virtualNetworks", \
            "targetResourceName": "MyVNet-target" \
        }'
```

List the move-resources in a move-collection.
```
az resource-mover move-resource list \
    --move-collection-name MyMoveCollection \
    --resource-group MyResourceGroup
```

Get the details of a move-resource.
```
az resource-mover move-resource show \
    --move-collection-name MyMoveCollection \
    --name MyMoveResource --resource-group MyResourceGroup
```

Delete a move-resource from the move-collection.
```
az resource-mover move-resource delete \
    --move-collection-name MyMoveCollection \
    --name MyMoveResource \
    --resource-group MyResourceGroup
```

## End-to-end Scenario
The following steps provide an end-to-end scenario, moving a vNet from a region to another with resource-mover CLI commands.

### Set environment variables
```
$collection_rg='CollectionRG',
$collection_name='MyMoveCollection',
$location='eastus2',
$source_region='eastus',
$target_region='westus',
$source_vnet='vnet-in-source-region',
$target_vnet='vnet-in-target-region',
$move_resource_vnet='vnet-as-move-resource',
$source_rg='SourceRG',
$target_rg='TargetRG',
$move_resource_rg='rg-as-move-resource'
```

### Prepare source resources to move
Create a resource group and a vNet in the resource group, as the source resources to move with resource-mover. After succeeding, set `$source_rg_id=@.id`, and set `$source_vnet_id=@.newVNet.id`
```
az group create -n ${source_rg} -l ${source_region}

az network vnet create \
    --resource-group ${source_rg} \
    --name ${source_vnet}
```

### Create a move-collection
Create a resource group and a move-collection in the resource group. After succeeding, set `$collection_principal_id=@.identity.principalId`, and set `$role_assignment_scope=/subscriptions/{subscriptionID}`
```
az group create -n ${collection_rg} -l ${location}

az resource-mover move-collection create \
    --location ${location} \
    --source-region ${source_region} \
    --target-region ${target_region} \
    --name ${collection_name} \
    --resource-group ${collection_rg} \
    --identity type=SystemAssigned
```

### Create role assignments for the move-collection
For the MoveCollection object to access the subscription in which the Azure Resource Mover service is located, it needs a system-assigned managed identity (formerly known as Managed Service Identity (MSI)) that's trusted by the subscription.
The identity is assigned the Contributor or the User Access Administrator role for the source subscription.
```
az role assignment create \
    --assignee-object-id $(collection_principal_id} \
    --role Contributor \
    --scope ${role_assignment_scope}

az role assignment create \
    --assignee-object-id ${collection_principal_id} \
    --role "User Access Administrator" \
    --scope ${role_assignment_scope}
```

### Add move-resources to the move-collection
Before the commands, prepare two json files with resource settings. For vNet, the contents of the file are like
```
{
    'resourceType': 'Microsoft.Network/virtualNetworks',
    'targetResourceName': 'vnet-in-target-region'
}
``` 
For resource-group, the contents of the file are like
```
{
    'resourceType': 'resourceGroups',
    'targetResourceName': 'TargetRG'
}
```
Then set `$vnet_resource_settings={the path of vNet json file}`, and `$rg_resource_settings={the path of resource group json file}`
```
az resource-mover move-resource add \
    --resource-group $(collection_rg} \
    --move-collection-name $(collection_name} \
    --name $(move_resource_vnet} \
    --source-id $(source_vnet_id} \
    --resource-settings $(vnet_resource_settings}

az resource-mover move-resource add \
    --resource-group $(collection_rg} \
    --move-collection-name $(collection_name} \
    --name $(move_resource_rg} \
    --source-id $(source_rg_id} \
    --resource-settings $(rg_resource_settings}
```

### List unresolved-dependencies and resolve the dependencies
```
az resource-mover move-collection list-unresolved-dependency \
    --resource-group $(collection_rg}
    --move-collection-name $(collection_name}

az resource-mover move-collection resolve-dependency \
    --resource-group $(collection_rg}
    --move-collection-name $(collection_name}
```

### Prepare
```
az resource-mover move-collection prepare \
    --move-resources $(move_resource_vnet_id} $(move_resource_rg_id} \
    --name $(collection_name} \
    --resource-group $(collection_rg}
```

### Initiate-move
```
az resource-mover move-collection initiate-move \
    --move-resources $(move_resource_vnet_id} $(move_resource_rg_id} \
    --name $(collection_name} \
    --resource-group $(collection_rg}
```

### Commit
```
az resource-mover move-collection commit \
    --move-resources $(move_resource_vnet_id} $(move_resource_rg_id} \
    --name $(collection_name} \
    --resource-group $(collection_rg}
```

### Check the resources in target region
```
az group show -n $(target_rg}
az network vnet show -g $(target_rg} -n $(target_vnet}
```

### Delete the source resources
```
az network vnet delete -g $(source_rg} -n $(source_vnet}
az group delete -g $(source_rg} --yes
```

### Delete the move-resources and move-collection
```
az resource-mover move-collection bulk-remove \
    --move-resources $(move_resource_vnet_id} $(move_resource_rg_id} \
    --name $(collection_name} \
    --resource-group $(collection_rg}

az resource-mover move-collection delete \
    --name $(collection_name} \
    --resource-group $(collection_rg} \
    --yes

az group delete -n $(collection_rg} --yes
```