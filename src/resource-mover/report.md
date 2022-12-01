# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az resource-mover|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az resource-mover` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az resource-mover move-collection|MoveCollections|[commands](#CommandsInMoveCollections)|
|az resource-mover move-collection|UnresolvedDependencies|[commands](#CommandsInUnresolvedDependencies)|
|az resource-mover move-resource|MoveResources|[commands](#CommandsInMoveResources)|

## COMMANDS
### <a name="CommandsInMoveCollections">Commands in `az resource-mover move-collection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resource-mover move-collection list](#MoveCollectionsListMoveCollectionsBySubscription)|ListMoveCollectionsBySubscription|[Parameters](#ParametersMoveCollectionsListMoveCollectionsBySubscription)|[Example](#ExamplesMoveCollectionsListMoveCollectionsBySubscription)|
|[az resource-mover move-collection show](#MoveCollectionsGet)|Get|[Parameters](#ParametersMoveCollectionsGet)|[Example](#ExamplesMoveCollectionsGet)|
|[az resource-mover move-collection create](#MoveCollectionsCreate)|Create|[Parameters](#ParametersMoveCollectionsCreate)|[Example](#ExamplesMoveCollectionsCreate)|
|[az resource-mover move-collection update](#MoveCollectionsUpdate)|Update|[Parameters](#ParametersMoveCollectionsUpdate)|[Example](#ExamplesMoveCollectionsUpdate)|
|[az resource-mover move-collection delete](#MoveCollectionsDelete)|Delete|[Parameters](#ParametersMoveCollectionsDelete)|[Example](#ExamplesMoveCollectionsDelete)|
|[az resource-mover move-collection bulk-remove](#MoveCollectionsBulkRemove)|BulkRemove|[Parameters](#ParametersMoveCollectionsBulkRemove)|[Example](#ExamplesMoveCollectionsBulkRemove)|
|[az resource-mover move-collection commit](#MoveCollectionsCommit)|Commit|[Parameters](#ParametersMoveCollectionsCommit)|[Example](#ExamplesMoveCollectionsCommit)|
|[az resource-mover move-collection discard](#MoveCollectionsDiscard)|Discard|[Parameters](#ParametersMoveCollectionsDiscard)|[Example](#ExamplesMoveCollectionsDiscard)|
|[az resource-mover move-collection initiate-move](#MoveCollectionsInitiateMove)|InitiateMove|[Parameters](#ParametersMoveCollectionsInitiateMove)|[Example](#ExamplesMoveCollectionsInitiateMove)|
|[az resource-mover move-collection list-required-for](#MoveCollectionsListRequiredFor)|ListRequiredFor|[Parameters](#ParametersMoveCollectionsListRequiredFor)|[Example](#ExamplesMoveCollectionsListRequiredFor)|
|[az resource-mover move-collection prepare](#MoveCollectionsPrepare)|Prepare|[Parameters](#ParametersMoveCollectionsPrepare)|[Example](#ExamplesMoveCollectionsPrepare)|
|[az resource-mover move-collection resolve-dependency](#MoveCollectionsResolveDependencies)|ResolveDependencies|[Parameters](#ParametersMoveCollectionsResolveDependencies)|[Example](#ExamplesMoveCollectionsResolveDependencies)|

### <a name="CommandsInUnresolvedDependencies">Commands in `az resource-mover move-collection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resource-mover move-collection list-unresolved-dependency](#UnresolvedDependenciesGet)|Get|[Parameters](#ParametersUnresolvedDependenciesGet)|[Example](#ExamplesUnresolvedDependenciesGet)|

### <a name="CommandsInMoveResources">Commands in `az resource-mover move-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resource-mover move-resource list](#MoveResourcesList)|List|[Parameters](#ParametersMoveResourcesList)|[Example](#ExamplesMoveResourcesList)|
|[az resource-mover move-resource show](#MoveResourcesGet)|Get|[Parameters](#ParametersMoveResourcesGet)|[Example](#ExamplesMoveResourcesGet)|
|[az resource-mover move-resource delete](#MoveResourcesDelete)|Delete|[Parameters](#ParametersMoveResourcesDelete)|[Example](#ExamplesMoveResourcesDelete)|
|[az resource-mover move-resource add](#MoveResourcesCreate)|Create|[Parameters](#ParametersMoveResourcesCreate)|[Example](#ExamplesMoveResourcesCreate)|


## COMMAND DETAILS
### group `az resource-mover move-collection`
#### <a name="MoveCollectionsListMoveCollectionsBySubscription">Command `az resource-mover move-collection list`</a>

##### <a name="ExamplesMoveCollectionsListMoveCollectionsBySubscription">Example</a>
```
az resource-mover move-collection list
```
##### <a name="ParametersMoveCollectionsListMoveCollectionsBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="MoveCollectionsGet">Command `az resource-mover move-collection show`</a>

##### <a name="ExamplesMoveCollectionsGet">Example</a>
```
az resource-mover move-collection show --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

#### <a name="MoveCollectionsCreate">Command `az resource-mover move-collection create`</a>

##### <a name="ExamplesMoveCollectionsCreate">Example</a>
```
az resource-mover move-collection create --identity type="SystemAssigned" --location "eastus2" --source-region \
"eastus" --target-region "westus" --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives.|location|location|
|**--identity**|object|Defines the MSI properties of the Move Collection.|identity|identity|
|**--source-region**|string|Gets or sets the source region.|source_region|sourceRegion|
|**--target-region**|string|Gets or sets the target region.|target_region|targetRegion|

#### <a name="MoveCollectionsUpdate">Command `az resource-mover move-collection update`</a>

##### <a name="ExamplesMoveCollectionsUpdate">Example</a>
```
az resource-mover move-collection update --identity type="SystemAssigned" --tags key1="mc1" --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--tags**|dictionary|Gets or sets the Resource tags.|tags|tags|
|**--identity**|object|Defines the MSI properties of the Move Collection.|identity|identity|

#### <a name="MoveCollectionsDelete">Command `az resource-mover move-collection delete`</a>

##### <a name="ExamplesMoveCollectionsDelete">Example</a>
```
az resource-mover move-collection delete --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

#### <a name="MoveCollectionsBulkRemove">Command `az resource-mover move-collection bulk-remove`</a>

##### <a name="ExamplesMoveCollectionsBulkRemove">Example</a>
```
az resource-mover move-collection bulk-remove --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Micro\
soft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name \
"movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsBulkRemove">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--move-collection-name**|string||move_collection_name|moveCollectionName|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsCommit">Command `az resource-mover move-collection commit`</a>

##### <a name="ExamplesMoveCollectionsCommit">Example</a>
```
az resource-mover move-collection commit --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.\
Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsCommit">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsDiscard">Command `az resource-mover move-collection discard`</a>

##### <a name="ExamplesMoveCollectionsDiscard">Example</a>
```
az resource-mover move-collection discard --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft\
.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsDiscard">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsInitiateMove">Command `az resource-mover move-collection initiate-move`</a>

##### <a name="ExamplesMoveCollectionsInitiateMove">Example</a>
```
az resource-mover move-collection initiate-move --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Mic\
rosoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name \
"movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsInitiateMove">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsListRequiredFor">Command `az resource-mover move-collection list-required-for`</a>

##### <a name="ExamplesMoveCollectionsListRequiredFor">Example</a>
```
az resource-mover move-collection list-required-for --name "movecollection1" --resource-group "rg1" --source-id \
"/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/nic1"
```
##### <a name="ParametersMoveCollectionsListRequiredFor">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--source-id**|string|The sourceId for which the api is invoked.|source_id|sourceId|

#### <a name="MoveCollectionsPrepare">Command `az resource-mover move-collection prepare`</a>

##### <a name="ExamplesMoveCollectionsPrepare">Example</a>
```
az resource-mover move-collection prepare --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft\
.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsPrepare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsResolveDependencies">Command `az resource-mover move-collection resolve-dependency`</a>

##### <a name="ExamplesMoveCollectionsResolveDependencies">Example</a>
```
az resource-mover move-collection resolve-dependency --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsResolveDependencies">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

### group `az resource-mover move-collection`
#### <a name="UnresolvedDependenciesGet">Command `az resource-mover move-collection list-unresolved-dependency`</a>

##### <a name="ExamplesUnresolvedDependenciesGet">Example</a>
```
az resource-mover move-collection list-unresolved-dependency --move-collection-name "movecollection1" --resource-group \
"rg1"
```
##### <a name="ParametersUnresolvedDependenciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--dependency-level**|choice|Defines the dependency level.|dependency_level|dependencyLevel|
|**--orderby**|string|OData order by query option. For example, you can use $orderby=Count desc.|orderby|$orderby|
|**--filter**|string|The filter to apply on the operation. For example, $apply=filter(count eq 2).|filter|$filter|

### group `az resource-mover move-resource`
#### <a name="MoveResourcesList">Command `az resource-mover move-resource list`</a>

##### <a name="ExamplesMoveResourcesList">Example</a>
```
az resource-mover move-resource list --move-collection-name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveResourcesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--filter**|string|The filter to apply on the operation. For example, you can use $filter=Properties/ProvisioningState eq 'Succeeded'.|filter|$filter|

#### <a name="MoveResourcesGet">Command `az resource-mover move-resource show`</a>

##### <a name="ExamplesMoveResourcesGet">Example</a>
```
az resource-mover move-resource show --move-collection-name "movecollection1" --name "moveresourcename1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveResourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resource-name**|string|The Move Resource Name.|move_resource_name|moveResourceName|

#### <a name="MoveResourcesDelete">Command `az resource-mover move-resource delete`</a>

##### <a name="ExamplesMoveResourcesDelete">Example</a>
```
az resource-mover move-resource delete --move-collection-name "movecollection1" --name "moveresourcename1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveResourcesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resource-name**|string|The Move Resource Name.|move_resource_name|moveResourceName|

#### <a name="MoveResourcesCreate">Command `az resource-mover move-resource add`</a>

##### <a name="ExamplesMoveResourcesCreate">Example</a>
```
az resource-mover move-resource add --depends-on-overrides id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/reso\
urceGroups/eastusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" target-id="/subscriptions/c4488a3f-a7f7-\
4ad4-aa72-0e1f4d9c0756/resourceGroups/westusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" \
--resource-settings "{\\"resourceType\\":\\"Microsoft.Compute/virtualMachines\\",\\"targetAvailabilitySetId\\":\\"/subs\
criptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/availabilitySets/avset1\\",\\"targetAvailabilityZon\
e\\":\\"2\\",\\"targetResourceName\\":\\"westusvm1\\",\\"targetVmSize\\":null,\\"userManagedIdentities\\":[\\"/subscrip\
tions/subid/resourceGroups/eastusRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/umi1\\"]}" --source-id \
"/subscriptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/virtualMachines/eastusvm1" \
--move-collection-name "movecollection1" --name "moveresourcename1" --resource-group "rg1"
```
##### <a name="ParametersMoveResourcesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resource-name**|string|The Move Resource Name.|move_resource_name|moveResourceName|
|**--source-id**|string|Gets or sets the Source ARM Id of the resource.|source_id|sourceId|
|**--existing-target-id**|string|Gets or sets the existing target ARM Id of the resource.|existing_target_id|existingTargetId|
|**--resource-settings**|object|Gets or sets the resource settings.|resource_settings|resourceSettings|
|**--depends-on-overrides**|array|Gets or sets the move resource dependencies overrides.|depends_on_overrides|dependsOnOverrides|
