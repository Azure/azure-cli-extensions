# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az devcenter|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az devcenter` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az devcenter attached-network|AttachedNetworks|[commands](#CommandsInAttachedNetworks)|
|az devcenter catalog|Catalogs|[commands](#CommandsInCatalogs)|
|az devcenter dev-box-definition|DevBoxDefinitions|[commands](#CommandsInDevBoxDefinitions)|
|az devcenter dev-center|DevCenters|[commands](#CommandsInDevCenters)|
|az devcenter environment-type|EnvironmentTypes|[commands](#CommandsInEnvironmentTypes)|
|az devcenter gallery|Galleries|[commands](#CommandsInGalleries)|
|az devcenter image|Images|[commands](#CommandsInImages)|
|az devcenter image-version|ImageVersions|[commands](#CommandsInImageVersions)|
|az devcenter network-connection|NetworkConnections|[commands](#CommandsInNetworkConnections)|
|az devcenter operation-statuses|OperationStatuses|[commands](#CommandsInOperationStatuses)|
|az devcenter pool|Pools|[commands](#CommandsInPools)|
|az devcenter project|Projects|[commands](#CommandsInProjects)|
|az devcenter project-environment-type|ProjectEnvironmentTypes|[commands](#CommandsInProjectEnvironmentTypes)|
|az devcenter schedule|Schedules|[commands](#CommandsInSchedules)|
|az devcenter sku|Skus|[commands](#CommandsInSkus)|
|az devcenter usage|Usages|[commands](#CommandsInUsages)|

## COMMANDS
### <a name="CommandsInAttachedNetworks">Commands in `az devcenter attached-network` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter attached-network list](#AttachedNetworksListByProject)|ListByProject|[Parameters](#ParametersAttachedNetworksListByProject)|[Example](#ExamplesAttachedNetworksListByProject)|
|[az devcenter attached-network list](#AttachedNetworksListByDevCenter)|ListByDevCenter|[Parameters](#ParametersAttachedNetworksListByDevCenter)|[Example](#ExamplesAttachedNetworksListByDevCenter)|
|[az devcenter attached-network show](#AttachedNetworksGetByProject)|GetByProject|[Parameters](#ParametersAttachedNetworksGetByProject)|[Example](#ExamplesAttachedNetworksGetByProject)|
|[az devcenter attached-network show](#AttachedNetworksGetByDevCenter)|GetByDevCenter|[Parameters](#ParametersAttachedNetworksGetByDevCenter)|[Example](#ExamplesAttachedNetworksGetByDevCenter)|
|[az devcenter attached-network create](#AttachedNetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAttachedNetworksCreateOrUpdate#Create)|[Example](#ExamplesAttachedNetworksCreateOrUpdate#Create)|
|[az devcenter attached-network update](#AttachedNetworksCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersAttachedNetworksCreateOrUpdate#Update)|Not Found|
|[az devcenter attached-network delete](#AttachedNetworksDelete)|Delete|[Parameters](#ParametersAttachedNetworksDelete)|[Example](#ExamplesAttachedNetworksDelete)|

### <a name="CommandsInCatalogs">Commands in `az devcenter catalog` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter catalog list](#CatalogsListByDevCenter)|ListByDevCenter|[Parameters](#ParametersCatalogsListByDevCenter)|[Example](#ExamplesCatalogsListByDevCenter)|
|[az devcenter catalog show](#CatalogsGet)|Get|[Parameters](#ParametersCatalogsGet)|[Example](#ExamplesCatalogsGet)|
|[az devcenter catalog create](#CatalogsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCatalogsCreateOrUpdate#Create)|[Example](#ExamplesCatalogsCreateOrUpdate#Create)|
|[az devcenter catalog update](#CatalogsUpdate)|Update|[Parameters](#ParametersCatalogsUpdate)|[Example](#ExamplesCatalogsUpdate)|
|[az devcenter catalog delete](#CatalogsDelete)|Delete|[Parameters](#ParametersCatalogsDelete)|[Example](#ExamplesCatalogsDelete)|
|[az devcenter catalog sync](#CatalogsSync)|Sync|[Parameters](#ParametersCatalogsSync)|[Example](#ExamplesCatalogsSync)|

### <a name="CommandsInDevBoxDefinitions">Commands in `az devcenter dev-box-definition` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter dev-box-definition list](#DevBoxDefinitionsListByDevCenter)|ListByDevCenter|[Parameters](#ParametersDevBoxDefinitionsListByDevCenter)|[Example](#ExamplesDevBoxDefinitionsListByDevCenter)|
|[az devcenter dev-box-definition list](#DevBoxDefinitionsListByProject)|ListByProject|[Parameters](#ParametersDevBoxDefinitionsListByProject)|[Example](#ExamplesDevBoxDefinitionsListByProject)|
|[az devcenter dev-box-definition show](#DevBoxDefinitionsGet)|Get|[Parameters](#ParametersDevBoxDefinitionsGet)|[Example](#ExamplesDevBoxDefinitionsGet)|
|[az devcenter dev-box-definition show](#DevBoxDefinitionsGetByProject)|GetByProject|[Parameters](#ParametersDevBoxDefinitionsGetByProject)|[Example](#ExamplesDevBoxDefinitionsGetByProject)|
|[az devcenter dev-box-definition create](#DevBoxDefinitionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDevBoxDefinitionsCreateOrUpdate#Create)|[Example](#ExamplesDevBoxDefinitionsCreateOrUpdate#Create)|
|[az devcenter dev-box-definition update](#DevBoxDefinitionsUpdate)|Update|[Parameters](#ParametersDevBoxDefinitionsUpdate)|[Example](#ExamplesDevBoxDefinitionsUpdate)|
|[az devcenter dev-box-definition delete](#DevBoxDefinitionsDelete)|Delete|[Parameters](#ParametersDevBoxDefinitionsDelete)|[Example](#ExamplesDevBoxDefinitionsDelete)|

### <a name="CommandsInDevCenters">Commands in `az devcenter dev-center` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter dev-center list](#DevCentersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDevCentersListByResourceGroup)|[Example](#ExamplesDevCentersListByResourceGroup)|
|[az devcenter dev-center list](#DevCentersListBySubscription)|ListBySubscription|[Parameters](#ParametersDevCentersListBySubscription)|[Example](#ExamplesDevCentersListBySubscription)|
|[az devcenter dev-center show](#DevCentersGet)|Get|[Parameters](#ParametersDevCentersGet)|[Example](#ExamplesDevCentersGet)|
|[az devcenter dev-center create](#DevCentersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDevCentersCreateOrUpdate#Create)|[Example](#ExamplesDevCentersCreateOrUpdate#Create)|
|[az devcenter dev-center update](#DevCentersUpdate)|Update|[Parameters](#ParametersDevCentersUpdate)|[Example](#ExamplesDevCentersUpdate)|
|[az devcenter dev-center delete](#DevCentersDelete)|Delete|[Parameters](#ParametersDevCentersDelete)|[Example](#ExamplesDevCentersDelete)|

### <a name="CommandsInEnvironmentTypes">Commands in `az devcenter environment-type` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter environment-type list](#EnvironmentTypesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersEnvironmentTypesListByDevCenter)|[Example](#ExamplesEnvironmentTypesListByDevCenter)|
|[az devcenter environment-type show](#EnvironmentTypesGet)|Get|[Parameters](#ParametersEnvironmentTypesGet)|[Example](#ExamplesEnvironmentTypesGet)|
|[az devcenter environment-type create](#EnvironmentTypesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersEnvironmentTypesCreateOrUpdate#Create)|[Example](#ExamplesEnvironmentTypesCreateOrUpdate#Create)|
|[az devcenter environment-type update](#EnvironmentTypesUpdate)|Update|[Parameters](#ParametersEnvironmentTypesUpdate)|[Example](#ExamplesEnvironmentTypesUpdate)|
|[az devcenter environment-type delete](#EnvironmentTypesDelete)|Delete|[Parameters](#ParametersEnvironmentTypesDelete)|[Example](#ExamplesEnvironmentTypesDelete)|

### <a name="CommandsInGalleries">Commands in `az devcenter gallery` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter gallery list](#GalleriesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersGalleriesListByDevCenter)|[Example](#ExamplesGalleriesListByDevCenter)|
|[az devcenter gallery show](#GalleriesGet)|Get|[Parameters](#ParametersGalleriesGet)|[Example](#ExamplesGalleriesGet)|
|[az devcenter gallery create](#GalleriesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersGalleriesCreateOrUpdate#Create)|[Example](#ExamplesGalleriesCreateOrUpdate#Create)|
|[az devcenter gallery update](#GalleriesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersGalleriesCreateOrUpdate#Update)|Not Found|
|[az devcenter gallery delete](#GalleriesDelete)|Delete|[Parameters](#ParametersGalleriesDelete)|[Example](#ExamplesGalleriesDelete)|

### <a name="CommandsInImages">Commands in `az devcenter image` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter image list](#ImagesListByGallery)|ListByGallery|[Parameters](#ParametersImagesListByGallery)|[Example](#ExamplesImagesListByGallery)|
|[az devcenter image list](#ImagesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersImagesListByDevCenter)|[Example](#ExamplesImagesListByDevCenter)|
|[az devcenter image show](#ImagesGet)|Get|[Parameters](#ParametersImagesGet)|[Example](#ExamplesImagesGet)|

### <a name="CommandsInImageVersions">Commands in `az devcenter image-version` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter image-version list](#ImageVersionsListByImage)|ListByImage|[Parameters](#ParametersImageVersionsListByImage)|[Example](#ExamplesImageVersionsListByImage)|
|[az devcenter image-version show](#ImageVersionsGet)|Get|[Parameters](#ParametersImageVersionsGet)|[Example](#ExamplesImageVersionsGet)|

### <a name="CommandsInNetworkConnections">Commands in `az devcenter network-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter network-connection list](#NetworkConnectionsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersNetworkConnectionsListByResourceGroup)|[Example](#ExamplesNetworkConnectionsListByResourceGroup)|
|[az devcenter network-connection list](#NetworkConnectionsListBySubscription)|ListBySubscription|[Parameters](#ParametersNetworkConnectionsListBySubscription)|[Example](#ExamplesNetworkConnectionsListBySubscription)|
|[az devcenter network-connection show](#NetworkConnectionsGet)|Get|[Parameters](#ParametersNetworkConnectionsGet)|[Example](#ExamplesNetworkConnectionsGet)|
|[az devcenter network-connection create](#NetworkConnectionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersNetworkConnectionsCreateOrUpdate#Create)|[Example](#ExamplesNetworkConnectionsCreateOrUpdate#Create)|
|[az devcenter network-connection update](#NetworkConnectionsUpdate)|Update|[Parameters](#ParametersNetworkConnectionsUpdate)|[Example](#ExamplesNetworkConnectionsUpdate)|
|[az devcenter network-connection delete](#NetworkConnectionsDelete)|Delete|[Parameters](#ParametersNetworkConnectionsDelete)|[Example](#ExamplesNetworkConnectionsDelete)|
|[az devcenter network-connection list-health-detail](#NetworkConnectionsListHealthDetails)|ListHealthDetails|[Parameters](#ParametersNetworkConnectionsListHealthDetails)|[Example](#ExamplesNetworkConnectionsListHealthDetails)|
|[az devcenter network-connection run-health-check](#NetworkConnectionsRunHealthChecks)|RunHealthChecks|[Parameters](#ParametersNetworkConnectionsRunHealthChecks)|[Example](#ExamplesNetworkConnectionsRunHealthChecks)|
|[az devcenter network-connection show-health-detail](#NetworkConnectionsGetHealthDetails)|GetHealthDetails|[Parameters](#ParametersNetworkConnectionsGetHealthDetails)|[Example](#ExamplesNetworkConnectionsGetHealthDetails)|

### <a name="CommandsInOperationStatuses">Commands in `az devcenter operation-statuses` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter operation-statuses show](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|

### <a name="CommandsInPools">Commands in `az devcenter pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter pool list](#PoolsListByProject)|ListByProject|[Parameters](#ParametersPoolsListByProject)|[Example](#ExamplesPoolsListByProject)|
|[az devcenter pool show](#PoolsGet)|Get|[Parameters](#ParametersPoolsGet)|[Example](#ExamplesPoolsGet)|
|[az devcenter pool create](#PoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersPoolsCreateOrUpdate#Create)|[Example](#ExamplesPoolsCreateOrUpdate#Create)|
|[az devcenter pool update](#PoolsUpdate)|Update|[Parameters](#ParametersPoolsUpdate)|[Example](#ExamplesPoolsUpdate)|
|[az devcenter pool delete](#PoolsDelete)|Delete|[Parameters](#ParametersPoolsDelete)|[Example](#ExamplesPoolsDelete)|

### <a name="CommandsInProjects">Commands in `az devcenter project` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter project list](#ProjectsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersProjectsListByResourceGroup)|[Example](#ExamplesProjectsListByResourceGroup)|
|[az devcenter project list](#ProjectsListBySubscription)|ListBySubscription|[Parameters](#ParametersProjectsListBySubscription)|[Example](#ExamplesProjectsListBySubscription)|
|[az devcenter project show](#ProjectsGet)|Get|[Parameters](#ParametersProjectsGet)|[Example](#ExamplesProjectsGet)|
|[az devcenter project create](#ProjectsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersProjectsCreateOrUpdate#Create)|[Example](#ExamplesProjectsCreateOrUpdate#Create)|
|[az devcenter project update](#ProjectsUpdate)|Update|[Parameters](#ParametersProjectsUpdate)|[Example](#ExamplesProjectsUpdate)|
|[az devcenter project delete](#ProjectsDelete)|Delete|[Parameters](#ParametersProjectsDelete)|[Example](#ExamplesProjectsDelete)|

### <a name="CommandsInProjectEnvironmentTypes">Commands in `az devcenter project-environment-type` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter project-environment-type list](#ProjectEnvironmentTypesList)|List|[Parameters](#ParametersProjectEnvironmentTypesList)|[Example](#ExamplesProjectEnvironmentTypesList)|
|[az devcenter project-environment-type show](#ProjectEnvironmentTypesGet)|Get|[Parameters](#ParametersProjectEnvironmentTypesGet)|[Example](#ExamplesProjectEnvironmentTypesGet)|
|[az devcenter project-environment-type create](#ProjectEnvironmentTypesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersProjectEnvironmentTypesCreateOrUpdate#Create)|[Example](#ExamplesProjectEnvironmentTypesCreateOrUpdate#Create)|
|[az devcenter project-environment-type update](#ProjectEnvironmentTypesUpdate)|Update|[Parameters](#ParametersProjectEnvironmentTypesUpdate)|[Example](#ExamplesProjectEnvironmentTypesUpdate)|
|[az devcenter project-environment-type delete](#ProjectEnvironmentTypesDelete)|Delete|[Parameters](#ParametersProjectEnvironmentTypesDelete)|[Example](#ExamplesProjectEnvironmentTypesDelete)|

### <a name="CommandsInSchedules">Commands in `az devcenter schedule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter schedule list](#SchedulesListByPool)|ListByPool|[Parameters](#ParametersSchedulesListByPool)|[Example](#ExamplesSchedulesListByPool)|
|[az devcenter schedule show](#SchedulesGet)|Get|[Parameters](#ParametersSchedulesGet)|[Example](#ExamplesSchedulesGet)|
|[az devcenter schedule create](#SchedulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSchedulesCreateOrUpdate#Create)|[Example](#ExamplesSchedulesCreateOrUpdate#Create)|
|[az devcenter schedule update](#SchedulesUpdate)|Update|[Parameters](#ParametersSchedulesUpdate)|[Example](#ExamplesSchedulesUpdate)|
|[az devcenter schedule delete](#SchedulesDelete)|Delete|[Parameters](#ParametersSchedulesDelete)|[Example](#ExamplesSchedulesDelete)|

### <a name="CommandsInSkus">Commands in `az devcenter sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter sku list](#SkusListBySubscription)|ListBySubscription|[Parameters](#ParametersSkusListBySubscription)|[Example](#ExamplesSkusListBySubscription)|

### <a name="CommandsInUsages">Commands in `az devcenter usage` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter usage list](#UsagesListByLocation)|ListByLocation|[Parameters](#ParametersUsagesListByLocation)|[Example](#ExamplesUsagesListByLocation)|


## COMMAND DETAILS
### group `az devcenter attached-network`
#### <a name="AttachedNetworksListByProject">Command `az devcenter attached-network list`</a>

##### <a name="ExamplesAttachedNetworksListByProject">Example</a>
```
az devcenter attached-network list --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="AttachedNetworksListByDevCenter">Command `az devcenter attached-network list`</a>

##### <a name="ExamplesAttachedNetworksListByDevCenter">Example</a>
```
az devcenter attached-network list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="AttachedNetworksGetByProject">Command `az devcenter attached-network show`</a>

##### <a name="ExamplesAttachedNetworksGetByProject">Example</a>
```
az devcenter attached-network show --attached-network-connection-name "network-uswest3" --project-name "{projectName}" \
--resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksGetByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--attached-network-connection-name**|string|The name of the attached NetworkConnection.|attached_network_connection_name|attachedNetworkConnectionName|

#### <a name="AttachedNetworksGetByDevCenter">Command `az devcenter attached-network show`</a>

##### <a name="ExamplesAttachedNetworksGetByDevCenter">Example</a>
```
az devcenter attached-network show --attached-network-connection-name "network-uswest3" --dev-center-name "Contoso" \
--resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksGetByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--attached-network-connection-name**|string|The name of the attached NetworkConnection.|attached_network_connection_name|attachedNetworkConnectionName|

#### <a name="AttachedNetworksCreateOrUpdate#Create">Command `az devcenter attached-network create`</a>

##### <a name="ExamplesAttachedNetworksCreateOrUpdate#Create">Example</a>
```
az devcenter attached-network create --attached-network-connection-name "{attachedNetworkConnectionName}" \
--network-connection-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/NetworkConnec\
tions/network-uswest3" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--attached-network-connection-name**|string|The name of the attached NetworkConnection.|attached_network_connection_name|attachedNetworkConnectionName|
|**--network-connection-id**|string|The resource ID of the NetworkConnection you want to attach.|network_connection_id|networkConnectionId|

#### <a name="AttachedNetworksCreateOrUpdate#Update">Command `az devcenter attached-network update`</a>


##### <a name="ParametersAttachedNetworksCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--attached-network-connection-name**|string|The name of the attached NetworkConnection.|attached_network_connection_name|attachedNetworkConnectionName|
|**--network-connection-id**|string|The resource ID of the NetworkConnection you want to attach.|network_connection_id|networkConnectionId|

#### <a name="AttachedNetworksDelete">Command `az devcenter attached-network delete`</a>

##### <a name="ExamplesAttachedNetworksDelete">Example</a>
```
az devcenter attached-network delete --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersAttachedNetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--attached-network-connection-name**|string|The name of the attached NetworkConnection.|attached_network_connection_name|attachedNetworkConnectionName|

### group `az devcenter catalog`
#### <a name="CatalogsListByDevCenter">Command `az devcenter catalog list`</a>

##### <a name="ExamplesCatalogsListByDevCenter">Example</a>
```
az devcenter catalog list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="CatalogsGet">Command `az devcenter catalog show`</a>

##### <a name="ExamplesCatalogsGet">Example</a>
```
az devcenter catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

#### <a name="CatalogsCreateOrUpdate#Create">Command `az devcenter catalog create`</a>

##### <a name="ExamplesCatalogsCreateOrUpdate#Create">Example</a>
```
az devcenter catalog create --ado-git path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.\
net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecontoso" --name \
"{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
az devcenter catalog create --git-hub path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.\
net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" --name "{catalogName}" \
--dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--git-hub**|object|Properties for a GitHub catalog type.|git_hub|gitHub|
|**--ado-git**|object|Properties for an Azure DevOps catalog type.|ado_git|adoGit|

#### <a name="CatalogsUpdate">Command `az devcenter catalog update`</a>

##### <a name="ExamplesCatalogsUpdate">Example</a>
```
az devcenter catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name "Contoso" \
--resource-group "rg1"
```
##### <a name="ParametersCatalogsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--git-hub**|object|Properties for a GitHub catalog type.|git_hub|gitHub|
|**--ado-git**|object|Properties for an Azure DevOps catalog type.|ado_git|adoGit|

#### <a name="CatalogsDelete">Command `az devcenter catalog delete`</a>

##### <a name="ExamplesCatalogsDelete">Example</a>
```
az devcenter catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

#### <a name="CatalogsSync">Command `az devcenter catalog sync`</a>

##### <a name="ExamplesCatalogsSync">Example</a>
```
az devcenter catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsSync">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

### group `az devcenter dev-box-definition`
#### <a name="DevBoxDefinitionsListByDevCenter">Command `az devcenter dev-box-definition list`</a>

##### <a name="ExamplesDevBoxDefinitionsListByDevCenter">Example</a>
```
az devcenter dev-box-definition list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevBoxDefinitionsListByProject">Command `az devcenter dev-box-definition list`</a>

##### <a name="ExamplesDevBoxDefinitionsListByProject">Example</a>
```
az devcenter dev-box-definition list --project-name "ContosoProject" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevBoxDefinitionsGet">Command `az devcenter dev-box-definition show`</a>

##### <a name="ExamplesDevBoxDefinitionsGet">Example</a>
```
az devcenter dev-box-definition show --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--dev-box-definition-name**|string|The name of the Dev Box definition.|dev_box_definition_name|devBoxDefinitionName|

#### <a name="DevBoxDefinitionsGetByProject">Command `az devcenter dev-box-definition show`</a>

##### <a name="ExamplesDevBoxDefinitionsGetByProject">Example</a>
```
az devcenter dev-box-definition show --name "WebDevBox" --project-name "ContosoProject" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsGetByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--dev-box-definition-name**|string|The name of the Dev Box definition.|dev_box_definition_name|devBoxDefinitionName|

#### <a name="DevBoxDefinitionsCreateOrUpdate#Create">Command `az devcenter dev-box-definition create`</a>

##### <a name="ExamplesDevBoxDefinitionsCreateOrUpdate#Create">Example</a>
```
az devcenter dev-box-definition create --location "centralus" --image-reference id="/subscriptions/0ac520ee-14c0-480f-b\
6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.DevCenter/devcenters/Contoso/galleries/contosogallery/images\
/exampleImage/version/1.0.0" --os-storage-type "SSD_1024" --sku name="Preview" --name "WebDevBox" --dev-center-name \
"Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--dev-box-definition-name**|string|The name of the Dev Box definition.|dev_box_definition_name|devBoxDefinitionName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--image-reference**|object|Image reference information.|image_reference|imageReference|
|**--sku**|object|The SKU for Dev Boxes created using this definition.|sku|sku|
|**--os-storage-type**|string|The storage type used for the Operating System disk of Dev Boxes created using this definition.|os_storage_type|osStorageType|

#### <a name="DevBoxDefinitionsUpdate">Command `az devcenter dev-box-definition update`</a>

##### <a name="ExamplesDevBoxDefinitionsUpdate">Example</a>
```
az devcenter dev-box-definition update --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourc\
eGroups/Example/providers/Microsoft.DevCenter/devcenters/Contoso/galleries/contosogallery/images/exampleImage/version/2\
.0.0" --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--dev-box-definition-name**|string|The name of the Dev Box definition.|dev_box_definition_name|devBoxDefinitionName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--image-reference**|object|Image reference information.|image_reference|imageReference|
|**--sku**|object|The SKU for Dev Boxes created using this definition.|sku|sku|
|**--os-storage-type**|string|The storage type used for the Operating System disk of Dev Boxes created using this definition.|os_storage_type|osStorageType|

#### <a name="DevBoxDefinitionsDelete">Command `az devcenter dev-box-definition delete`</a>

##### <a name="ExamplesDevBoxDefinitionsDelete">Example</a>
```
az devcenter dev-box-definition delete --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevBoxDefinitionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--dev-box-definition-name**|string|The name of the Dev Box definition.|dev_box_definition_name|devBoxDefinitionName|

### group `az devcenter dev-center`
#### <a name="DevCentersListByResourceGroup">Command `az devcenter dev-center list`</a>

##### <a name="ExamplesDevCentersListByResourceGroup">Example</a>
```
az devcenter dev-center list --resource-group "rg1"
```
##### <a name="ParametersDevCentersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevCentersListBySubscription">Command `az devcenter dev-center list`</a>

##### <a name="ExamplesDevCentersListBySubscription">Example</a>
```
az devcenter dev-center list
```
##### <a name="ParametersDevCentersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevCentersGet">Command `az devcenter dev-center show`</a>

##### <a name="ExamplesDevCentersGet">Example</a>
```
az devcenter dev-center show --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|

#### <a name="DevCentersCreateOrUpdate#Create">Command `az devcenter dev-center create`</a>

##### <a name="ExamplesDevCentersCreateOrUpdate#Create">Example</a>
```
az devcenter dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
az devcenter dev-center create --type "UserAssigned" --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-\
0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\
\\":{}}" --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--type**|choice|Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed).|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="DevCentersUpdate">Command `az devcenter dev-center update`</a>

##### <a name="ExamplesDevCentersUpdate">Example</a>
```
az devcenter dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--type**|choice|Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed).|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="DevCentersDelete">Command `az devcenter dev-center delete`</a>

##### <a name="ExamplesDevCentersDelete">Example</a>
```
az devcenter dev-center delete --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|

### group `az devcenter environment-type`
#### <a name="EnvironmentTypesListByDevCenter">Command `az devcenter environment-type list`</a>

##### <a name="ExamplesEnvironmentTypesListByDevCenter">Example</a>
```
az devcenter environment-type list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="EnvironmentTypesGet">Command `az devcenter environment-type show`</a>

##### <a name="ExamplesEnvironmentTypesGet">Example</a>
```
az devcenter environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

#### <a name="EnvironmentTypesCreateOrUpdate#Create">Command `az devcenter environment-type create`</a>

##### <a name="ExamplesEnvironmentTypesCreateOrUpdate#Create">Example</a>
```
az devcenter environment-type create --tags Owner="superuser" --dev-center-name "Contoso" --name \
"{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="EnvironmentTypesUpdate">Command `az devcenter environment-type update`</a>

##### <a name="ExamplesEnvironmentTypesUpdate">Example</a>
```
az devcenter environment-type update --tags Owner="superuser" --dev-center-name "Contoso" --name \
"{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="EnvironmentTypesDelete">Command `az devcenter environment-type delete`</a>

##### <a name="ExamplesEnvironmentTypesDelete">Example</a>
```
az devcenter environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

### group `az devcenter gallery`
#### <a name="GalleriesListByDevCenter">Command `az devcenter gallery list`</a>

##### <a name="ExamplesGalleriesListByDevCenter">Example</a>
```
az devcenter gallery list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersGalleriesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="GalleriesGet">Command `az devcenter gallery show`</a>

##### <a name="ExamplesGalleriesGet">Example</a>
```
az devcenter gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|

#### <a name="GalleriesCreateOrUpdate#Create">Command `az devcenter gallery create`</a>

##### <a name="ExamplesGalleriesCreateOrUpdate#Create">Example</a>
```
az devcenter gallery create --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microso\
ft.Compute/galleries/{galleryName}" --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--gallery-resource-id**|string|The resource ID of the backing Azure Compute Gallery.|gallery_resource_id|galleryResourceId|

#### <a name="GalleriesCreateOrUpdate#Update">Command `az devcenter gallery update`</a>


##### <a name="ParametersGalleriesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--gallery-resource-id**|string|The resource ID of the backing Azure Compute Gallery.|gallery_resource_id|galleryResourceId|

#### <a name="GalleriesDelete">Command `az devcenter gallery delete`</a>

##### <a name="ExamplesGalleriesDelete">Example</a>
```
az devcenter gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|

### group `az devcenter image`
#### <a name="ImagesListByGallery">Command `az devcenter image list`</a>

##### <a name="ExamplesImagesListByGallery">Example</a>
```
az devcenter image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
```
##### <a name="ParametersImagesListByGallery">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ImagesListByDevCenter">Command `az devcenter image list`</a>

##### <a name="ExamplesImagesListByDevCenter">Example</a>
```
az devcenter image list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersImagesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ImagesGet">Command `az devcenter image show`</a>

##### <a name="ExamplesImagesGet">Example</a>
```
az devcenter image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name "{imageName}" \
--resource-group "rg1"
```
##### <a name="ParametersImagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--image-name**|string|The name of the image.|image_name|imageName|

### group `az devcenter image-version`
#### <a name="ImageVersionsListByImage">Command `az devcenter image-version list`</a>

##### <a name="ExamplesImageVersionsListByImage">Example</a>
```
az devcenter image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
--resource-group "rg1"
```
##### <a name="ParametersImageVersionsListByImage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--image-name**|string|The name of the image.|image_name|imageName|

#### <a name="ImageVersionsGet">Command `az devcenter image-version show`</a>

##### <a name="ExamplesImageVersionsGet">Example</a>
```
az devcenter image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
--resource-group "rg1" --version-name "{versionName}"
```
##### <a name="ParametersImageVersionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--image-name**|string|The name of the image.|image_name|imageName|
|**--version-name**|string|The version of the image.|version_name|versionName|

### group `az devcenter network-connection`
#### <a name="NetworkConnectionsListByResourceGroup">Command `az devcenter network-connection list`</a>

##### <a name="ExamplesNetworkConnectionsListByResourceGroup">Example</a>
```
az devcenter network-connection list --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="NetworkConnectionsListBySubscription">Command `az devcenter network-connection list`</a>

##### <a name="ExamplesNetworkConnectionsListBySubscription">Example</a>
```
az devcenter network-connection list
```
##### <a name="ParametersNetworkConnectionsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="NetworkConnectionsGet">Command `az devcenter network-connection show`</a>

##### <a name="ExamplesNetworkConnectionsGet">Example</a>
```
az devcenter network-connection show --name "uswest3network" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|

#### <a name="NetworkConnectionsCreateOrUpdate#Create">Command `az devcenter network-connection create`</a>

##### <a name="ExamplesNetworkConnectionsCreateOrUpdate#Create">Example</a>
```
az devcenter network-connection create --location "centralus" --domain-join-type "HybridAzureADJoin" --domain-name \
"mydomaincontroller.local" --domain-password "Password value for user" --domain-username \
"testuser@mydomaincontroller.local" --networking-resource-group-name "NetworkInterfaces" --subnet-id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/virtualNetwor\
ks/ExampleVNet/subnets/default" --name "uswest3network" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--subnet-id**|string|The subnet to attach Virtual Machines to|subnet_id|subnetId|
|**--domain-name**|string|Active Directory domain name|domain_name|domainName|
|**--organization-unit**|string|Active Directory domain Organization Unit (OU)|organization_unit|organizationUnit|
|**--domain-username**|string|The username of an Active Directory account (user or service account) that has permissions to create computer objects in Active Directory. Required format: admin@contoso.com.|domain_username|domainUsername|
|**--domain-password**|string|The password for the account used to join domain|domain_password|domainPassword|
|**--networking-resource-group-name**|string|The name for resource group where NICs will be placed.|networking_resource_group_name|networkingResourceGroupName|
|**--domain-join-type**|choice|AAD Join type.|domain_join_type|domainJoinType|

#### <a name="NetworkConnectionsUpdate">Command `az devcenter network-connection update`</a>

##### <a name="ExamplesNetworkConnectionsUpdate">Example</a>
```
az devcenter network-connection update --domain-password "New Password value for user" --name "uswest3network" \
--resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--subnet-id**|string|The subnet to attach Virtual Machines to|subnet_id|subnetId|
|**--domain-name**|string|Active Directory domain name|domain_name|domainName|
|**--organization-unit**|string|Active Directory domain Organization Unit (OU)|organization_unit|organizationUnit|
|**--domain-username**|string|The username of an Active Directory account (user or service account) that has permissions to create computer objects in Active Directory. Required format: admin@contoso.com.|domain_username|domainUsername|
|**--domain-password**|string|The password for the account used to join domain|domain_password|domainPassword|

#### <a name="NetworkConnectionsDelete">Command `az devcenter network-connection delete`</a>

##### <a name="ExamplesNetworkConnectionsDelete">Example</a>
```
az devcenter network-connection delete --name "{networkConnectionName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|

#### <a name="NetworkConnectionsListHealthDetails">Command `az devcenter network-connection list-health-detail`</a>

##### <a name="ExamplesNetworkConnectionsListHealthDetails">Example</a>
```
az devcenter network-connection list-health-detail --name "uswest3network" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsListHealthDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|

#### <a name="NetworkConnectionsRunHealthChecks">Command `az devcenter network-connection run-health-check`</a>

##### <a name="ExamplesNetworkConnectionsRunHealthChecks">Example</a>
```
az devcenter network-connection run-health-check --name "uswest3network" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsRunHealthChecks">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|

#### <a name="NetworkConnectionsGetHealthDetails">Command `az devcenter network-connection show-health-detail`</a>

##### <a name="ExamplesNetworkConnectionsGetHealthDetails">Example</a>
```
az devcenter network-connection show-health-detail --name "{networkConnectionName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkConnectionsGetHealthDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-connection-name**|string|Name of the Network Connection that can be applied to a Pool.|network_connection_name|networkConnectionName|

### group `az devcenter operation-statuses`
#### <a name="OperationStatusesGet">Command `az devcenter operation-statuses show`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az devcenter operation-statuses show --operation-id "{operationId}" --location "{location}"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
|**--operation-id**|string|The ID of an ongoing async operation|operation_id|operationId|

### group `az devcenter pool`
#### <a name="PoolsListByProject">Command `az devcenter pool list`</a>

##### <a name="ExamplesPoolsListByProject">Example</a>
```
az devcenter pool list --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="PoolsGet">Command `az devcenter pool show`</a>

##### <a name="ExamplesPoolsGet">Example</a>
```
az devcenter pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|

#### <a name="PoolsCreateOrUpdate#Create">Command `az devcenter pool create`</a>

##### <a name="ExamplesPoolsCreateOrUpdate#Create">Example</a>
```
az devcenter pool create --location "centralus" --dev-box-definition-name "WebDevBox" --local-administrator "Enabled" \
--network-connection-name "Network1-westus2" --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--dev-box-definition-name**|string|Name of a Dev Box definition in parent Project of this Pool|dev_box_definition_name|devBoxDefinitionName|
|**--network-connection-name**|string|Name of a Network Connection in parent Project of this Pool|network_connection_name|networkConnectionName|
|**--local-administrator**|choice|Indicates whether owners of Dev Boxes in this pool are added as local administrators on the Dev Box.|local_administrator|localAdministrator|

#### <a name="PoolsUpdate">Command `az devcenter pool update`</a>

##### <a name="ExamplesPoolsUpdate">Example</a>
```
az devcenter pool update --dev-box-definition-name "WebDevBox2" --name "{poolName}" --project-name "{projectName}" \
--resource-group "rg1"
```
##### <a name="ParametersPoolsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--dev-box-definition-name**|string|Name of a Dev Box definition in parent Project of this Pool|dev_box_definition_name|devBoxDefinitionName|
|**--network-connection-name**|string|Name of a Network Connection in parent Project of this Pool|network_connection_name|networkConnectionName|
|**--local-administrator**|choice|Indicates whether owners of Dev Boxes in this pool are added as local administrators on the Dev Box.|local_administrator|localAdministrator|

#### <a name="PoolsDelete">Command `az devcenter pool delete`</a>

##### <a name="ExamplesPoolsDelete">Example</a>
```
az devcenter pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|

### group `az devcenter project`
#### <a name="ProjectsListByResourceGroup">Command `az devcenter project list`</a>

##### <a name="ExamplesProjectsListByResourceGroup">Example</a>
```
az devcenter project list --resource-group "rg1"
```
##### <a name="ParametersProjectsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ProjectsListBySubscription">Command `az devcenter project list`</a>

##### <a name="ExamplesProjectsListBySubscription">Example</a>
```
az devcenter project list
```
##### <a name="ParametersProjectsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ProjectsGet">Command `az devcenter project show`</a>

##### <a name="ExamplesProjectsGet">Example</a>
```
az devcenter project show --name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersProjectsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|

#### <a name="ProjectsCreateOrUpdate#Create">Command `az devcenter project create`</a>

##### <a name="ExamplesProjectsCreateOrUpdate#Create">Example</a>
```
az devcenter project create --location "centralus" --description "This is my first project." --dev-center-id \
"/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/devcenters/{devCenterName}" --tags \
CostCenter="R&D" --name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersProjectsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--dev-center-id**|string|Resource Id of an associated DevCenter|dev_center_id|devCenterId|
|**--description**|string|Description of the project.|description|description|

#### <a name="ProjectsUpdate">Command `az devcenter project update`</a>

##### <a name="ExamplesProjectsUpdate">Example</a>
```
az devcenter project update --description "This is my first project." --tags CostCenter="R&D" --name "{projectName}" \
--resource-group "rg1"
```
##### <a name="ParametersProjectsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--dev-center-id**|string|Resource Id of an associated DevCenter|dev_center_id|devCenterId|
|**--description**|string|Description of the project.|description|description|

#### <a name="ProjectsDelete">Command `az devcenter project delete`</a>

##### <a name="ExamplesProjectsDelete">Example</a>
```
az devcenter project delete --name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersProjectsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|

### group `az devcenter project-environment-type`
#### <a name="ProjectEnvironmentTypesList">Command `az devcenter project-environment-type list`</a>

##### <a name="ExamplesProjectEnvironmentTypesList">Example</a>
```
az devcenter project-environment-type list --project-name "ContosoProj" --resource-group "rg1"
```
##### <a name="ParametersProjectEnvironmentTypesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ProjectEnvironmentTypesGet">Command `az devcenter project-environment-type show`</a>

##### <a name="ExamplesProjectEnvironmentTypesGet">Example</a>
```
az devcenter project-environment-type show --environment-type-name "{environmentTypeName}" --project-name \
"ContosoProj" --resource-group "rg1"
```
##### <a name="ParametersProjectEnvironmentTypesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

#### <a name="ProjectEnvironmentTypesCreateOrUpdate#Create">Command `az devcenter project-environment-type create`</a>

##### <a name="ExamplesProjectEnvironmentTypesCreateOrUpdate#Create">Example</a>
```
az devcenter project-environment-type create --type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1\\":{}}" --creator-role-assignment "/some/role/definition/id" \
--deployment-target-id "/subscriptions/00000000-0000-0000-0000-000000000000" --status "Enabled" \
--user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c-e750-441c-98a7-10da8387e\
4d6\\":{}}}}" --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" --project-name "ContosoProj" \
--resource-group "rg1"
```
##### <a name="ParametersProjectEnvironmentTypesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location for the environment type|location|location|
|**--deployment-target-id**|string|Id of a subscription that the environment type will be mapped to. The environment's resources will be deployed into this subscription.|deployment_target_id|deploymentTargetId|
|**--status**|choice|Defines whether this Environment Type can be used in this Project.|status|status|
|**--creator-role-assignment**|string|The role definition assigned to the environment creator on backing resources.|creator_role_assignment|creatorRoleAssignment|
|**--user-role-assignments**|dictionary|Role Assignments created on environment backing resources. This is a mapping from a user object ID to an object of role definition IDs.|user_role_assignments|userRoleAssignments|
|**--type**|choice|Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed).|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="ProjectEnvironmentTypesUpdate">Command `az devcenter project-environment-type update`</a>

##### <a name="ExamplesProjectEnvironmentTypesUpdate">Example</a>
```
az devcenter project-environment-type update --type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1\\":{}}" --deployment-target-id "/subscriptions/00000000-0000-0000-0000-00000000\
0000" --status "Enabled" --user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c\
-e750-441c-98a7-10da8387e4d6\\":{}}}}" --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" \
--project-name "ContosoProj" --resource-group "rg1"
```
##### <a name="ParametersProjectEnvironmentTypesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--deployment-target-id**|string|Id of a subscription that the environment type will be mapped to. The environment's resources will be deployed into this subscription.|deployment_target_id|deploymentTargetId|
|**--status**|choice|Defines whether this Environment Type can be used in this Project.|status|status|
|**--creator-role-assignment**|string|The role definition assigned to the environment creator on backing resources.|creator_role_assignment|creatorRoleAssignment|
|**--user-role-assignments**|dictionary|Role Assignments created on environment backing resources. This is a mapping from a user object ID to an object of role definition IDs.|user_role_assignments|userRoleAssignments|
|**--type**|choice|Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed).|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="ProjectEnvironmentTypesDelete">Command `az devcenter project-environment-type delete`</a>

##### <a name="ExamplesProjectEnvironmentTypesDelete">Example</a>
```
az devcenter project-environment-type delete --environment-type-name "{environmentTypeName}" --project-name \
"ContosoProj" --resource-group "rg1"
```
##### <a name="ParametersProjectEnvironmentTypesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

### group `az devcenter schedule`
#### <a name="SchedulesListByPool">Command `az devcenter schedule list`</a>

##### <a name="ExamplesSchedulesListByPool">Example</a>
```
az devcenter schedule list --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1"
```
##### <a name="ParametersSchedulesListByPool">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="SchedulesGet">Command `az devcenter schedule show`</a>

##### <a name="ExamplesSchedulesGet">Example</a>
```
az devcenter schedule show --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" --name \
"autoShutdown"
```
##### <a name="ParametersSchedulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--schedule-name**|string|The name of the schedule that uniquely identifies it.|schedule_name|scheduleName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="SchedulesCreateOrUpdate#Create">Command `az devcenter schedule create`</a>

##### <a name="ExamplesSchedulesCreateOrUpdate#Create">Example</a>
```
az devcenter schedule create --state "Enabled" --time "17:30" --time-zone "America/Los_Angeles" --pool-name "DevPool" \
--project-name "DevProject" --resource-group "rg1" --name "autoShutdown"
```
##### <a name="ParametersSchedulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--schedule-name**|string|The name of the schedule that uniquely identifies it.|schedule_name|scheduleName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|
|**--time**|string|The target time to trigger the action. The format is HH:MM.|time|time|
|**--time-zone**|string|The IANA timezone id at which the schedule should execute.|time_zone|timeZone|
|**--state**|choice|Indicates whether or not this scheduled task is enabled.|state|state|

#### <a name="SchedulesUpdate">Command `az devcenter schedule update`</a>

##### <a name="ExamplesSchedulesUpdate">Example</a>
```
az devcenter schedule update --time "18:00" --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown"
```
##### <a name="ParametersSchedulesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--schedule-name**|string|The name of the schedule that uniquely identifies it.|schedule_name|scheduleName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--time**|string|The target time to trigger the action. The format is HH:MM.|time|time|
|**--time-zone**|string|The IANA timezone id at which the schedule should execute.|time_zone|timeZone|
|**--state**|choice|Indicates whether or not this scheduled task is enabled.|state|state|

#### <a name="SchedulesDelete">Command `az devcenter schedule delete`</a>

##### <a name="ExamplesSchedulesDelete">Example</a>
```
az devcenter schedule delete --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" --name \
"autoShutdown"
```
##### <a name="ParametersSchedulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--schedule-name**|string|The name of the schedule that uniquely identifies it.|schedule_name|scheduleName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

### group `az devcenter sku`
#### <a name="SkusListBySubscription">Command `az devcenter sku list`</a>

##### <a name="ExamplesSkusListBySubscription">Example</a>
```
az devcenter sku list
```
##### <a name="ParametersSkusListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

### group `az devcenter usage`
#### <a name="UsagesListByLocation">Command `az devcenter usage list`</a>

##### <a name="ExamplesUsagesListByLocation">Example</a>
```
az devcenter usage list --location "westus"
```
##### <a name="ParametersUsagesListByLocation">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
