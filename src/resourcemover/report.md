# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az resourcemover|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az resourcemover` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az resourcemover move-collection|MoveCollections|[commands](#CommandsInMoveCollections)|
|az resourcemover move-resource|MoveResources|[commands](#CommandsInMoveResources)|
|az resourcemover unresolved-dependency|UnresolvedDependencies|[commands](#CommandsInUnresolvedDependencies)|
|az resourcemover operation-discovery|OperationsDiscovery|[commands](#CommandsInOperationsDiscovery)|

## COMMANDS
### <a name="CommandsInMoveCollections">Commands in `az resourcemover move-collection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resourcemover move-collection show](#MoveCollectionsGet)|Get|[Parameters](#ParametersMoveCollectionsGet)|[Example](#ExamplesMoveCollectionsGet)|
|[az resourcemover move-collection create](#MoveCollectionsCreate)|Create|[Parameters](#ParametersMoveCollectionsCreate)|[Example](#ExamplesMoveCollectionsCreate)|
|[az resourcemover move-collection update](#MoveCollectionsUpdate)|Update|[Parameters](#ParametersMoveCollectionsUpdate)|[Example](#ExamplesMoveCollectionsUpdate)|
|[az resourcemover move-collection delete](#MoveCollectionsDelete)|Delete|[Parameters](#ParametersMoveCollectionsDelete)|[Example](#ExamplesMoveCollectionsDelete)|
|[az resourcemover move-collection bulk-remove](#MoveCollectionsBulkRemove)|BulkRemove|[Parameters](#ParametersMoveCollectionsBulkRemove)|[Example](#ExamplesMoveCollectionsBulkRemove)|
|[az resourcemover move-collection commit](#MoveCollectionsCommit)|Commit|[Parameters](#ParametersMoveCollectionsCommit)|[Example](#ExamplesMoveCollectionsCommit)|
|[az resourcemover move-collection discard](#MoveCollectionsDiscard)|Discard|[Parameters](#ParametersMoveCollectionsDiscard)|[Example](#ExamplesMoveCollectionsDiscard)|
|[az resourcemover move-collection initiate-move](#MoveCollectionsInitiateMove)|InitiateMove|[Parameters](#ParametersMoveCollectionsInitiateMove)|[Example](#ExamplesMoveCollectionsInitiateMove)|
|[az resourcemover move-collection list-move-collection](#MoveCollectionsListMoveCollectionsByResourceGroup)|ListMoveCollectionsByResourceGroup|[Parameters](#ParametersMoveCollectionsListMoveCollectionsByResourceGroup)|[Example](#ExamplesMoveCollectionsListMoveCollectionsByResourceGroup)|
|[az resourcemover move-collection list-move-collection](#MoveCollectionsListMoveCollectionsBySubscription)|ListMoveCollectionsBySubscription|[Parameters](#ParametersMoveCollectionsListMoveCollectionsBySubscription)|[Example](#ExamplesMoveCollectionsListMoveCollectionsBySubscription)|
|[az resourcemover move-collection prepare](#MoveCollectionsPrepare)|Prepare|[Parameters](#ParametersMoveCollectionsPrepare)|[Example](#ExamplesMoveCollectionsPrepare)|
|[az resourcemover move-collection resolve-dependency](#MoveCollectionsResolveDependencies)|ResolveDependencies|[Parameters](#ParametersMoveCollectionsResolveDependencies)|[Example](#ExamplesMoveCollectionsResolveDependencies)|

### <a name="CommandsInMoveResources">Commands in `az resourcemover move-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resourcemover move-resource list](#MoveResourcesList)|List|[Parameters](#ParametersMoveResourcesList)|[Example](#ExamplesMoveResourcesList)|
|[az resourcemover move-resource show](#MoveResourcesGet)|Get|[Parameters](#ParametersMoveResourcesGet)|[Example](#ExamplesMoveResourcesGet)|
|[az resourcemover move-resource create](#MoveResourcesCreate)|Create|[Parameters](#ParametersMoveResourcesCreate)|[Example](#ExamplesMoveResourcesCreate)|
|[az resourcemover move-resource delete](#MoveResourcesDelete)|Delete|[Parameters](#ParametersMoveResourcesDelete)|[Example](#ExamplesMoveResourcesDelete)|

### <a name="CommandsInOperationsDiscovery">Commands in `az resourcemover operation-discovery` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resourcemover operation-discovery show](#OperationsDiscoveryGet)|Get|[Parameters](#ParametersOperationsDiscoveryGet)|[Example](#ExamplesOperationsDiscoveryGet)|

### <a name="CommandsInUnresolvedDependencies">Commands in `az resourcemover unresolved-dependency` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az resourcemover unresolved-dependency show](#UnresolvedDependenciesGet)|Get|[Parameters](#ParametersUnresolvedDependenciesGet)|[Example](#ExamplesUnresolvedDependenciesGet)|


## COMMAND DETAILS

### group `az resourcemover move-collection`
#### <a name="MoveCollectionsGet">Command `az resourcemover move-collection show`</a>

##### <a name="ExamplesMoveCollectionsGet">Example</a>
```
az resourcemover move-collection show --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

#### <a name="MoveCollectionsCreate">Command `az resourcemover move-collection create`</a>

##### <a name="ExamplesMoveCollectionsCreate">Example</a>
```
az resourcemover move-collection create --identity type="SystemAssigned" --location "eastus2" --properties \
source-region="eastus" target-region="westus" --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives.|location|location|
|**--identity**|object|Defines the MSI properties of the Move Collection.|identity|identity|
|**--properties**|object|Defines the move collection properties.|properties|properties|

#### <a name="MoveCollectionsUpdate">Command `az resourcemover move-collection update`</a>

##### <a name="ExamplesMoveCollectionsUpdate">Example</a>
```
az resourcemover move-collection update --identity type="SystemAssigned" --tags key1="mc1" --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--tags**|dictionary|Gets or sets the Resource tags.|tags|tags|
|**--identity**|object|Defines the MSI properties of the Move Collection.|identity|identity|

#### <a name="MoveCollectionsDelete">Command `az resourcemover move-collection delete`</a>

##### <a name="ExamplesMoveCollectionsDelete">Example</a>
```
az resourcemover move-collection delete --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

#### <a name="MoveCollectionsBulkRemove">Command `az resourcemover move-collection bulk-remove`</a>

##### <a name="ExamplesMoveCollectionsBulkRemove">Example</a>
```
az resourcemover move-collection bulk-remove --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Micros\
oft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name \
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

#### <a name="MoveCollectionsCommit">Command `az resourcemover move-collection commit`</a>

##### <a name="ExamplesMoveCollectionsCommit">Example</a>
```
az resourcemover move-collection commit --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.M\
igrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsCommit">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsDiscard">Command `az resourcemover move-collection discard`</a>

##### <a name="ExamplesMoveCollectionsDiscard">Example</a>
```
az resourcemover move-collection discard --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.\
Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsDiscard">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsInitiateMove">Command `az resourcemover move-collection initiate-move`</a>

##### <a name="ExamplesMoveCollectionsInitiateMove">Example</a>
```
az resourcemover move-collection initiate-move --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Micr\
osoft.Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name \
"movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsInitiateMove">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsListMoveCollectionsByResourceGroup">Command `az resourcemover move-collection list-move-collection`</a>

##### <a name="ExamplesMoveCollectionsListMoveCollectionsByResourceGroup">Example</a>
```
az resourcemover move-collection list-move-collection --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsListMoveCollectionsByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|

#### <a name="MoveCollectionsListMoveCollectionsBySubscription">Command `az resourcemover move-collection list-move-collection`</a>

##### <a name="ExamplesMoveCollectionsListMoveCollectionsBySubscription">Example</a>
```
az resourcemover move-collection list-move-collection
```
##### <a name="ParametersMoveCollectionsListMoveCollectionsBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MoveCollectionsPrepare">Command `az resourcemover move-collection prepare`</a>

##### <a name="ExamplesMoveCollectionsPrepare">Example</a>
```
az resourcemover move-collection prepare --move-resources "/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.\
Migrate/MoveCollections/movecollection1/MoveResources/moveresource1" --validate-only false --name "movecollection1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsPrepare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--validate-only**|boolean|Gets or sets a value indicating whether the operation needs to only run pre-requisite.|validate_only|validateOnly|
|**--move-resources**|array|Gets or sets the list of resource Id's, by default it accepts move resource id's unless the input type is switched via moveResourceInputType property.|move_resources|moveResources|
|**--move-resource-input-type**|choice|Defines the move resource input type.|move_resource_input_type|moveResourceInputType|

#### <a name="MoveCollectionsResolveDependencies">Command `az resourcemover move-collection resolve-dependency`</a>

##### <a name="ExamplesMoveCollectionsResolveDependencies">Example</a>
```
az resourcemover move-collection resolve-dependency --name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveCollectionsResolveDependencies">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|

### group `az resourcemover move-resource`
#### <a name="MoveResourcesList">Command `az resourcemover move-resource list`</a>

##### <a name="ExamplesMoveResourcesList">Example</a>
```
az resourcemover move-resource list --move-collection-name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersMoveResourcesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--filter**|string|The filter to apply on the operation. For example, you can use $filter=Properties/ProvisioningState eq 'Succeeded'.|filter|$filter|

#### <a name="MoveResourcesGet">Command `az resourcemover move-resource show`</a>

##### <a name="ExamplesMoveResourcesGet">Example</a>
```
az resourcemover move-resource show --move-collection-name "movecollection1" --name "moveresourcename1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveResourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resource-name**|string|The Move Resource Name.|move_resource_name|moveResourceName|

#### <a name="MoveResourcesCreate">Command `az resourcemover move-resource create`</a>

##### <a name="ExamplesMoveResourcesCreate">Example</a>
```
az resourcemover move-resource create --depends-on-overrides id="/subscriptions/c4488a3f-a7f7-4ad4-aa72-0e1f4d9c0756/re\
sourceGroups/eastusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" target-id="/subscriptions/c4488a3f-a7f\
7-4ad4-aa72-0e1f4d9c0756/resourceGroups/westusRG/providers/Microsoft.Network/networkInterfaces/eastusvm140" \
--resource-settings "{\\"resourceType\\":\\"Microsoft.Compute/virtualMachines\\",\\"targetAvailabilitySetId\\":\\"/subs\
criptions/subid/resourceGroups/eastusRG/providers/Microsoft.Compute/availabilitySets/avset1\\",\\"targetAvailabilityZon\
e\\":\\"2\\",\\"targetResourceName\\":\\"westusvm1\\",\\"targetVmSize\\":null}" --source-id \
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

#### <a name="MoveResourcesDelete">Command `az resourcemover move-resource delete`</a>

##### <a name="ExamplesMoveResourcesDelete">Example</a>
```
az resourcemover move-resource delete --move-collection-name "movecollection1" --name "moveresourcename1" \
--resource-group "rg1"
```
##### <a name="ParametersMoveResourcesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
|**--move-resource-name**|string|The Move Resource Name.|move_resource_name|moveResourceName|

### group `az resourcemover operation-discovery`
#### <a name="OperationsDiscoveryGet">Command `az resourcemover operation-discovery show`</a>

##### <a name="ExamplesOperationsDiscoveryGet">Example</a>
```
az resourcemover operation-discovery show
```
##### <a name="ParametersOperationsDiscoveryGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az resourcemover unresolved-dependency`
#### <a name="UnresolvedDependenciesGet">Command `az resourcemover unresolved-dependency show`</a>

##### <a name="ExamplesUnresolvedDependenciesGet">Example</a>
```
az resourcemover unresolved-dependency show --move-collection-name "movecollection1" --resource-group "rg1"
```
##### <a name="ParametersUnresolvedDependenciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name.|resource_group_name|resourceGroupName|
|**--move-collection-name**|string|The Move Collection Name.|move_collection_name|moveCollectionName|
