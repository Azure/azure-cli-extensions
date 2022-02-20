# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az fidalgo|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az fidalgo` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az fidalgo catalog|Catalogs|[commands](#CommandsInCatalogs)|
|az fidalgo catalog-item|CatalogItems|[commands](#CommandsInCatalogItems)|
|az fidalgo deployment|Deployments|[commands](#CommandsInDeployments)|
|az fidalgo dev-center|DevCenters|[commands](#CommandsInDevCenters)|
|az fidalgo environment|Environments|[commands](#CommandsInEnvironments)|
|az fidalgo environment-type|EnvironmentTypes|[commands](#CommandsInEnvironmentTypes)|
|az fidalgo gallery|Galleries|[commands](#CommandsInGalleries)|
|az fidalgo image|Images|[commands](#CommandsInImages)|
|az fidalgo image-version|ImageVersions|[commands](#CommandsInImageVersions)|
|az fidalgo machine-definition|MachineDefinitions|[commands](#CommandsInMachineDefinitions)|
|az fidalgo mapping|Mappings|[commands](#CommandsInMappings)|
|az fidalgo network-setting|NetworkSettings|[commands](#CommandsInNetworkSettings)|
|az fidalgo operation-statuses|OperationStatuses|[commands](#CommandsInOperationStatuses)|
|az fidalgo pool|Pools|[commands](#CommandsInPools)|
|az fidalgo project|Projects|[commands](#CommandsInProjects)|
|az fidalgo sku|Skus|[commands](#CommandsInSkus)|

## COMMANDS
### <a name="CommandsInCatalogs">Commands in `az fidalgo catalog` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo catalog list](#CatalogsListByDevCenter)|ListByDevCenter|[Parameters](#ParametersCatalogsListByDevCenter)|[Example](#ExamplesCatalogsListByDevCenter)|
|[az fidalgo catalog show](#CatalogsGet)|Get|[Parameters](#ParametersCatalogsGet)|[Example](#ExamplesCatalogsGet)|
|[az fidalgo catalog create](#CatalogsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCatalogsCreateOrUpdate#Create)|[Example](#ExamplesCatalogsCreateOrUpdate#Create)|
|[az fidalgo catalog update](#CatalogsUpdate)|Update|[Parameters](#ParametersCatalogsUpdate)|[Example](#ExamplesCatalogsUpdate)|
|[az fidalgo catalog delete](#CatalogsDelete)|Delete|[Parameters](#ParametersCatalogsDelete)|[Example](#ExamplesCatalogsDelete)|
|[az fidalgo catalog sync](#CatalogsSync)|Sync|[Parameters](#ParametersCatalogsSync)|[Example](#ExamplesCatalogsSync)|

### <a name="CommandsInCatalogItems">Commands in `az fidalgo catalog-item` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo catalog-item list](#CatalogItemsListByCatalog)|ListByCatalog|[Parameters](#ParametersCatalogItemsListByCatalog)|[Example](#ExamplesCatalogItemsListByCatalog)|
|[az fidalgo catalog-item list](#CatalogItemsListByProject)|ListByProject|[Parameters](#ParametersCatalogItemsListByProject)|[Example](#ExamplesCatalogItemsListByProject)|
|[az fidalgo catalog-item show](#CatalogItemsGet)|Get|[Parameters](#ParametersCatalogItemsGet)|[Example](#ExamplesCatalogItemsGet)|
|[az fidalgo catalog-item create](#CatalogItemsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCatalogItemsCreateOrUpdate#Create)|[Example](#ExamplesCatalogItemsCreateOrUpdate#Create)|
|[az fidalgo catalog-item update](#CatalogItemsUpdate)|Update|[Parameters](#ParametersCatalogItemsUpdate)|[Example](#ExamplesCatalogItemsUpdate)|
|[az fidalgo catalog-item delete](#CatalogItemsDelete)|Delete|[Parameters](#ParametersCatalogItemsDelete)|[Example](#ExamplesCatalogItemsDelete)|

### <a name="CommandsInDeployments">Commands in `az fidalgo deployment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo deployment list](#DeploymentsListByEnvironment)|ListByEnvironment|[Parameters](#ParametersDeploymentsListByEnvironment)|[Example](#ExamplesDeploymentsListByEnvironment)|

### <a name="CommandsInDevCenters">Commands in `az fidalgo dev-center` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo dev-center list](#DevCentersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDevCentersListByResourceGroup)|[Example](#ExamplesDevCentersListByResourceGroup)|
|[az fidalgo dev-center list](#DevCentersListBySubscription)|ListBySubscription|[Parameters](#ParametersDevCentersListBySubscription)|[Example](#ExamplesDevCentersListBySubscription)|
|[az fidalgo dev-center show](#DevCentersGet)|Get|[Parameters](#ParametersDevCentersGet)|[Example](#ExamplesDevCentersGet)|
|[az fidalgo dev-center create](#DevCentersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDevCentersCreateOrUpdate#Create)|[Example](#ExamplesDevCentersCreateOrUpdate#Create)|
|[az fidalgo dev-center update](#DevCentersUpdate)|Update|[Parameters](#ParametersDevCentersUpdate)|[Example](#ExamplesDevCentersUpdate)|
|[az fidalgo dev-center delete](#DevCentersDelete)|Delete|[Parameters](#ParametersDevCentersDelete)|[Example](#ExamplesDevCentersDelete)|

### <a name="CommandsInEnvironments">Commands in `az fidalgo environment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo environment list](#EnvironmentsListByProject)|ListByProject|[Parameters](#ParametersEnvironmentsListByProject)|[Example](#ExamplesEnvironmentsListByProject)|
|[az fidalgo environment show](#EnvironmentsGet)|Get|[Parameters](#ParametersEnvironmentsGet)|[Example](#ExamplesEnvironmentsGet)|
|[az fidalgo environment create](#EnvironmentsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersEnvironmentsCreateOrUpdate#Create)|[Example](#ExamplesEnvironmentsCreateOrUpdate#Create)|
|[az fidalgo environment update](#EnvironmentsUpdate)|Update|[Parameters](#ParametersEnvironmentsUpdate)|[Example](#ExamplesEnvironmentsUpdate)|
|[az fidalgo environment delete](#EnvironmentsDelete)|Delete|[Parameters](#ParametersEnvironmentsDelete)|[Example](#ExamplesEnvironmentsDelete)|
|[az fidalgo environment deploy](#EnvironmentsDeploy)|Deploy|[Parameters](#ParametersEnvironmentsDeploy)|[Example](#ExamplesEnvironmentsDeploy)|

### <a name="CommandsInEnvironmentTypes">Commands in `az fidalgo environment-type` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo environment-type list](#EnvironmentTypesListByProject)|ListByProject|[Parameters](#ParametersEnvironmentTypesListByProject)|[Example](#ExamplesEnvironmentTypesListByProject)|
|[az fidalgo environment-type list](#EnvironmentTypesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersEnvironmentTypesListByDevCenter)|[Example](#ExamplesEnvironmentTypesListByDevCenter)|
|[az fidalgo environment-type show](#EnvironmentTypesGet)|Get|[Parameters](#ParametersEnvironmentTypesGet)|[Example](#ExamplesEnvironmentTypesGet)|
|[az fidalgo environment-type create](#EnvironmentTypesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersEnvironmentTypesCreateOrUpdate#Create)|[Example](#ExamplesEnvironmentTypesCreateOrUpdate#Create)|
|[az fidalgo environment-type update](#EnvironmentTypesUpdate)|Update|[Parameters](#ParametersEnvironmentTypesUpdate)|[Example](#ExamplesEnvironmentTypesUpdate)|
|[az fidalgo environment-type delete](#EnvironmentTypesDelete)|Delete|[Parameters](#ParametersEnvironmentTypesDelete)|[Example](#ExamplesEnvironmentTypesDelete)|

### <a name="CommandsInGalleries">Commands in `az fidalgo gallery` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo gallery list](#GalleriesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersGalleriesListByDevCenter)|[Example](#ExamplesGalleriesListByDevCenter)|
|[az fidalgo gallery show](#GalleriesGet)|Get|[Parameters](#ParametersGalleriesGet)|[Example](#ExamplesGalleriesGet)|
|[az fidalgo gallery create](#GalleriesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersGalleriesCreateOrUpdate#Create)|[Example](#ExamplesGalleriesCreateOrUpdate#Create)|
|[az fidalgo gallery update](#GalleriesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersGalleriesCreateOrUpdate#Update)|Not Found|
|[az fidalgo gallery delete](#GalleriesDelete)|Delete|[Parameters](#ParametersGalleriesDelete)|[Example](#ExamplesGalleriesDelete)|

### <a name="CommandsInImages">Commands in `az fidalgo image` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo image list](#ImagesListByGallery)|ListByGallery|[Parameters](#ParametersImagesListByGallery)|[Example](#ExamplesImagesListByGallery)|
|[az fidalgo image list](#ImagesListByDevCenter)|ListByDevCenter|[Parameters](#ParametersImagesListByDevCenter)|[Example](#ExamplesImagesListByDevCenter)|
|[az fidalgo image show](#ImagesGet)|Get|[Parameters](#ParametersImagesGet)|[Example](#ExamplesImagesGet)|

### <a name="CommandsInImageVersions">Commands in `az fidalgo image-version` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo image-version list](#ImageVersionsListByImage)|ListByImage|[Parameters](#ParametersImageVersionsListByImage)|[Example](#ExamplesImageVersionsListByImage)|
|[az fidalgo image-version show](#ImageVersionsGet)|Get|[Parameters](#ParametersImageVersionsGet)|[Example](#ExamplesImageVersionsGet)|

### <a name="CommandsInMachineDefinitions">Commands in `az fidalgo machine-definition` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo machine-definition list](#MachineDefinitionsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMachineDefinitionsListByResourceGroup)|[Example](#ExamplesMachineDefinitionsListByResourceGroup)|
|[az fidalgo machine-definition list](#MachineDefinitionsListBySubscription)|ListBySubscription|[Parameters](#ParametersMachineDefinitionsListBySubscription)|[Example](#ExamplesMachineDefinitionsListBySubscription)|
|[az fidalgo machine-definition show](#MachineDefinitionsGet)|Get|[Parameters](#ParametersMachineDefinitionsGet)|[Example](#ExamplesMachineDefinitionsGet)|
|[az fidalgo machine-definition create](#MachineDefinitionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMachineDefinitionsCreateOrUpdate#Create)|[Example](#ExamplesMachineDefinitionsCreateOrUpdate#Create)|
|[az fidalgo machine-definition update](#MachineDefinitionsUpdate)|Update|[Parameters](#ParametersMachineDefinitionsUpdate)|[Example](#ExamplesMachineDefinitionsUpdate)|
|[az fidalgo machine-definition delete](#MachineDefinitionsDelete)|Delete|[Parameters](#ParametersMachineDefinitionsDelete)|[Example](#ExamplesMachineDefinitionsDelete)|

### <a name="CommandsInMappings">Commands in `az fidalgo mapping` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo mapping list](#MappingsListByDevCenter)|ListByDevCenter|[Parameters](#ParametersMappingsListByDevCenter)|[Example](#ExamplesMappingsListByDevCenter)|
|[az fidalgo mapping show](#MappingsGet)|Get|[Parameters](#ParametersMappingsGet)|[Example](#ExamplesMappingsGet)|
|[az fidalgo mapping create](#MappingsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMappingsCreateOrUpdate#Create)|[Example](#ExamplesMappingsCreateOrUpdate#Create)|
|[az fidalgo mapping update](#MappingsUpdate)|Update|[Parameters](#ParametersMappingsUpdate)|[Example](#ExamplesMappingsUpdate)|
|[az fidalgo mapping delete](#MappingsDelete)|Delete|[Parameters](#ParametersMappingsDelete)|[Example](#ExamplesMappingsDelete)|

### <a name="CommandsInNetworkSettings">Commands in `az fidalgo network-setting` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo network-setting list](#NetworkSettingsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersNetworkSettingsListByResourceGroup)|[Example](#ExamplesNetworkSettingsListByResourceGroup)|
|[az fidalgo network-setting list](#NetworkSettingsListBySubscription)|ListBySubscription|[Parameters](#ParametersNetworkSettingsListBySubscription)|[Example](#ExamplesNetworkSettingsListBySubscription)|
|[az fidalgo network-setting show](#NetworkSettingsGet)|Get|[Parameters](#ParametersNetworkSettingsGet)|[Example](#ExamplesNetworkSettingsGet)|
|[az fidalgo network-setting create](#NetworkSettingsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersNetworkSettingsCreateOrUpdate#Create)|[Example](#ExamplesNetworkSettingsCreateOrUpdate#Create)|
|[az fidalgo network-setting update](#NetworkSettingsUpdate)|Update|[Parameters](#ParametersNetworkSettingsUpdate)|[Example](#ExamplesNetworkSettingsUpdate)|
|[az fidalgo network-setting delete](#NetworkSettingsDelete)|Delete|[Parameters](#ParametersNetworkSettingsDelete)|[Example](#ExamplesNetworkSettingsDelete)|
|[az fidalgo network-setting list-health-detail](#NetworkSettingsListHealthDetails)|ListHealthDetails|[Parameters](#ParametersNetworkSettingsListHealthDetails)|[Example](#ExamplesNetworkSettingsListHealthDetails)|
|[az fidalgo network-setting show-health-detail](#NetworkSettingsGetHealthDetails)|GetHealthDetails|[Parameters](#ParametersNetworkSettingsGetHealthDetails)|[Example](#ExamplesNetworkSettingsGetHealthDetails)|

### <a name="CommandsInOperationStatuses">Commands in `az fidalgo operation-statuses` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo operation-statuses show](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|

### <a name="CommandsInPools">Commands in `az fidalgo pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo pool list](#PoolsListByProject)|ListByProject|[Parameters](#ParametersPoolsListByProject)|[Example](#ExamplesPoolsListByProject)|
|[az fidalgo pool show](#PoolsGet)|Get|[Parameters](#ParametersPoolsGet)|[Example](#ExamplesPoolsGet)|
|[az fidalgo pool create](#PoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersPoolsCreateOrUpdate#Create)|[Example](#ExamplesPoolsCreateOrUpdate#Create)|
|[az fidalgo pool update](#PoolsUpdate)|Update|[Parameters](#ParametersPoolsUpdate)|[Example](#ExamplesPoolsUpdate)|
|[az fidalgo pool delete](#PoolsDelete)|Delete|[Parameters](#ParametersPoolsDelete)|[Example](#ExamplesPoolsDelete)|

### <a name="CommandsInProjects">Commands in `az fidalgo project` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo project list](#ProjectsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersProjectsListByResourceGroup)|[Example](#ExamplesProjectsListByResourceGroup)|
|[az fidalgo project list](#ProjectsListBySubscription)|ListBySubscription|[Parameters](#ParametersProjectsListBySubscription)|[Example](#ExamplesProjectsListBySubscription)|
|[az fidalgo project show](#ProjectsGet)|Get|[Parameters](#ParametersProjectsGet)|[Example](#ExamplesProjectsGet)|
|[az fidalgo project create](#ProjectsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersProjectsCreateOrUpdate#Create)|[Example](#ExamplesProjectsCreateOrUpdate#Create)|
|[az fidalgo project update](#ProjectsUpdate)|Update|[Parameters](#ParametersProjectsUpdate)|[Example](#ExamplesProjectsUpdate)|
|[az fidalgo project delete](#ProjectsDelete)|Delete|[Parameters](#ParametersProjectsDelete)|[Example](#ExamplesProjectsDelete)|

### <a name="CommandsInSkus">Commands in `az fidalgo sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az fidalgo sku list](#SkusListBySubscription)|ListBySubscription|[Parameters](#ParametersSkusListBySubscription)|[Example](#ExamplesSkusListBySubscription)|


## COMMAND DETAILS
### group `az fidalgo catalog`
#### <a name="CatalogsListByDevCenter">Command `az fidalgo catalog list`</a>

##### <a name="ExamplesCatalogsListByDevCenter">Example</a>
```
az fidalgo catalog list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="CatalogsGet">Command `az fidalgo catalog show`</a>

##### <a name="ExamplesCatalogsGet">Example</a>
```
az fidalgo catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

#### <a name="CatalogsCreateOrUpdate#Create">Command `az fidalgo catalog create`</a>

##### <a name="ExamplesCatalogsCreateOrUpdate#Create">Example</a>
```
az fidalgo catalog create --ado-git path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.ne\
t/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecontoso" --name \
"{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
az fidalgo catalog create --git-hub path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.ne\
t/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" --name "{catalogName}" \
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

#### <a name="CatalogsUpdate">Command `az fidalgo catalog update`</a>

##### <a name="ExamplesCatalogsUpdate">Example</a>
```
az fidalgo catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name "Contoso" \
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

#### <a name="CatalogsDelete">Command `az fidalgo catalog delete`</a>

##### <a name="ExamplesCatalogsDelete">Example</a>
```
az fidalgo catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

#### <a name="CatalogsSync">Command `az fidalgo catalog sync`</a>

##### <a name="ExamplesCatalogsSync">Example</a>
```
az fidalgo catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogsSync">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|

### group `az fidalgo catalog-item`
#### <a name="CatalogItemsListByCatalog">Command `az fidalgo catalog-item list`</a>

##### <a name="ExamplesCatalogItemsListByCatalog">Example</a>
```
az fidalgo catalog-item list --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogItemsListByCatalog">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="CatalogItemsListByProject">Command `az fidalgo catalog-item list`</a>

##### <a name="ExamplesCatalogItemsListByProject">Example</a>
```
az fidalgo catalog-item list --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersCatalogItemsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="CatalogItemsGet">Command `az fidalgo catalog-item show`</a>

##### <a name="ExamplesCatalogItemsGet">Example</a>
```
az fidalgo catalog-item show --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
--resource-group "rg1"
```
##### <a name="ParametersCatalogItemsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|The name of the catalog item.|catalog_item_name|catalogItemName|

#### <a name="CatalogItemsCreateOrUpdate#Create">Command `az fidalgo catalog-item create`</a>

##### <a name="ExamplesCatalogItemsCreateOrUpdate#Create">Example</a>
```
az fidalgo catalog-item create --description "Hello world template to deploy a basic API service" --parameters \
name="app_name" type="string" description="The name of the application. This must be provided when deploying an \
environment with this template." --template-path "azuredeploy.json" --name "{itemName}" --catalog-name "{catalogName}" \
--dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogItemsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|The name of the catalog item.|catalog_item_name|catalogItemName|
|**--description**|string|Description of the catalog item.|description|description|
|**--template-path**|string|Path to the catalog item entrypoint file.|template_path|templatePath|
|**--parameters**|array|Parameters that can be provided to the catalog item.|parameters|parameters|

#### <a name="CatalogItemsUpdate">Command `az fidalgo catalog-item update`</a>

##### <a name="ExamplesCatalogItemsUpdate">Example</a>
```
az fidalgo catalog-item update --description "Hello world template to deploy a basic API service" --name "{itemName}" \
--catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersCatalogItemsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|The name of the catalog item.|catalog_item_name|catalogItemName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of the catalog item.|description|description|

#### <a name="CatalogItemsDelete">Command `az fidalgo catalog-item delete`</a>

##### <a name="ExamplesCatalogItemsDelete">Example</a>
```
az fidalgo catalog-item delete --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
--resource-group "rg1"
```
##### <a name="ParametersCatalogItemsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--catalog-name**|string|The name of the Catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|The name of the catalog item.|catalog_item_name|catalogItemName|

### group `az fidalgo deployment`
#### <a name="DeploymentsListByEnvironment">Command `az fidalgo deployment list`</a>

##### <a name="ExamplesDeploymentsListByEnvironment">Example</a>
```
az fidalgo deployment list --environment-name "{environmentName}" --project-name "{projectName}" --resource-group \
"rg1"
```
##### <a name="ParametersDeploymentsListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

### group `az fidalgo dev-center`
#### <a name="DevCentersListByResourceGroup">Command `az fidalgo dev-center list`</a>

##### <a name="ExamplesDevCentersListByResourceGroup">Example</a>
```
az fidalgo dev-center list --resource-group "rg1"
```
##### <a name="ParametersDevCentersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevCentersListBySubscription">Command `az fidalgo dev-center list`</a>

##### <a name="ExamplesDevCentersListBySubscription">Example</a>
```
az fidalgo dev-center list
```
##### <a name="ParametersDevCentersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="DevCentersGet">Command `az fidalgo dev-center show`</a>

##### <a name="ExamplesDevCentersGet">Example</a>
```
az fidalgo dev-center show --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|

#### <a name="DevCentersCreateOrUpdate#Create">Command `az fidalgo dev-center create`</a>

##### <a name="ExamplesDevCentersCreateOrUpdate#Create">Example</a>
```
az fidalgo dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
az fidalgo dev-center create --type "UserAssigned" --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-00\
00-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\\
":{}}" --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--type**|choice|The type of identity used for the resource. The type 'SystemAssigned, UserAssigned' includes both an implicitly created identity and a user assigned identity. The type 'None' will remove any identities from the resource.|type|type|
|**--user-assigned-identities**|dictionary|The list of user identities associated with the resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

#### <a name="DevCentersUpdate">Command `az fidalgo dev-center update`</a>

##### <a name="ExamplesDevCentersUpdate">Example</a>
```
az fidalgo dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--type**|choice|The type of identity used for the resource. The type 'SystemAssigned, UserAssigned' includes both an implicitly created identity and a user assigned identity. The type 'None' will remove any identities from the resource.|type|type|
|**--user-assigned-identities**|dictionary|The list of user identities associated with the resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

#### <a name="DevCentersDelete">Command `az fidalgo dev-center delete`</a>

##### <a name="ExamplesDevCentersDelete">Example</a>
```
az fidalgo dev-center delete --name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersDevCentersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|

### group `az fidalgo environment`
#### <a name="EnvironmentsListByProject">Command `az fidalgo environment list`</a>

##### <a name="ExamplesEnvironmentsListByProject">Example</a>
```
az fidalgo environment list --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="EnvironmentsGet">Command `az fidalgo environment show`</a>

##### <a name="ExamplesEnvironmentsGet">Example</a>
```
az fidalgo environment show --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|

#### <a name="EnvironmentsCreateOrUpdate#Create">Command `az fidalgo environment create`</a>

##### <a name="ExamplesEnvironmentsCreateOrUpdate#Create">Example</a>
```
az fidalgo environment create --location "centralus" --description "Personal Dev Environment" --catalog-item-name \
"helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type "DevTest" --tags \
ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" \
--resource-group "rg1"
az fidalgo environment create --location "centralus" --description "Personal Dev Environment" --deployment-parameters \
"{\\"app_name\\":\\"mydevApi\\"}" --environment-type "DevTest" --template-uri "https://raw.githubusercontent.com/contos\
o/webhelpcenter/master/environments/composition-template.json" --tags ProjectType="WebApi" Role="Development" \
Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of the Environment.|description|description|
|**--catalog-item-name**|string|Name of the catalog item.|catalog_item_name|catalogItemName|
|**--template-uri**|string|Uri of a template used to deploy resources to the environment.|template_uri|templateUri|
|**--deployment-parameters**|any|Deployment parameters passed to catalog item.|deployment_parameters|deploymentParameters|
|**--environment-type**|string|Environment type.|environment_type|environmentType|

#### <a name="EnvironmentsUpdate">Command `az fidalgo environment update`</a>

##### <a name="ExamplesEnvironmentsUpdate">Example</a>
```
az fidalgo environment update --description "Personal Dev Environment 2" --tags ProjectType="WebApi" \
Role="Development" Tech="NetCore" --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--description**|string|Description of the Environment.|description|description|
|**--catalog-item-name**|string|Name of the catalog item.|catalog_item_name|catalogItemName|
|**--template-uri**|string|Uri of a template used to deploy resources to the environment.|template_uri|templateUri|
|**--deployment-parameters**|any|Deployment parameters passed to catalog item.|deployment_parameters|deploymentParameters|

#### <a name="EnvironmentsDelete">Command `az fidalgo environment delete`</a>

##### <a name="ExamplesEnvironmentsDelete">Example</a>
```
az fidalgo environment delete --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|

#### <a name="EnvironmentsDeploy">Command `az fidalgo environment deploy`</a>

##### <a name="ExamplesEnvironmentsDeploy">Example</a>
```
az fidalgo environment deploy --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsDeploy">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--parameters**|any|Deployment parameters passed to catalog item.|parameters|parameters|

### group `az fidalgo environment-type`
#### <a name="EnvironmentTypesListByProject">Command `az fidalgo environment-type list`</a>

##### <a name="ExamplesEnvironmentTypesListByProject">Example</a>
```
az fidalgo environment-type list --project-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="EnvironmentTypesListByDevCenter">Command `az fidalgo environment-type list`</a>

##### <a name="ExamplesEnvironmentTypesListByDevCenter">Example</a>
```
az fidalgo environment-type list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="EnvironmentTypesGet">Command `az fidalgo environment-type show`</a>

##### <a name="ExamplesEnvironmentTypesGet">Example</a>
```
az fidalgo environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

#### <a name="EnvironmentTypesCreateOrUpdate#Create">Command `az fidalgo environment-type create`</a>

##### <a name="ExamplesEnvironmentTypesCreateOrUpdate#Create">Example</a>
```
az fidalgo environment-type create --description "Developer/Testing environment" --dev-center-name "Contoso" --name \
"{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of the environment type.|description|description|

#### <a name="EnvironmentTypesUpdate">Command `az fidalgo environment-type update`</a>

##### <a name="ExamplesEnvironmentTypesUpdate">Example</a>
```
az fidalgo environment-type update --description "Updated description" --dev-center-name "Contoso" --name \
"{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of the environment type.|description|description|

#### <a name="EnvironmentTypesDelete">Command `az fidalgo environment-type delete`</a>

##### <a name="ExamplesEnvironmentTypesDelete">Example</a>
```
az fidalgo environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentTypesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--environment-type-name**|string|The name of the environment type.|environment_type_name|environmentTypeName|

### group `az fidalgo gallery`
#### <a name="GalleriesListByDevCenter">Command `az fidalgo gallery list`</a>

##### <a name="ExamplesGalleriesListByDevCenter">Example</a>
```
az fidalgo gallery list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersGalleriesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="GalleriesGet">Command `az fidalgo gallery show`</a>

##### <a name="ExamplesGalleriesGet">Example</a>
```
az fidalgo gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|

#### <a name="GalleriesCreateOrUpdate#Create">Command `az fidalgo gallery create`</a>

##### <a name="ExamplesGalleriesCreateOrUpdate#Create">Example</a>
```
az fidalgo gallery create --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft\
.Compute/galleries/{galleryName}" --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--gallery-resource-id**|string|The resource ID of the backing Azure Compute Gallery.|gallery_resource_id|galleryResourceId|

#### <a name="GalleriesCreateOrUpdate#Update">Command `az fidalgo gallery update`</a>


##### <a name="ParametersGalleriesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--gallery-resource-id**|string|The resource ID of the backing Azure Compute Gallery.|gallery_resource_id|galleryResourceId|

#### <a name="GalleriesDelete">Command `az fidalgo gallery delete`</a>

##### <a name="ExamplesGalleriesDelete">Example</a>
```
az fidalgo gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### <a name="ParametersGalleriesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|

### group `az fidalgo image`
#### <a name="ImagesListByGallery">Command `az fidalgo image list`</a>

##### <a name="ExamplesImagesListByGallery">Example</a>
```
az fidalgo image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
```
##### <a name="ParametersImagesListByGallery">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ImagesListByDevCenter">Command `az fidalgo image list`</a>

##### <a name="ExamplesImagesListByDevCenter">Example</a>
```
az fidalgo image list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersImagesListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ImagesGet">Command `az fidalgo image show`</a>

##### <a name="ExamplesImagesGet">Example</a>
```
az fidalgo image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name "{imageName}" \
--resource-group "rg1"
```
##### <a name="ParametersImagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--image-name**|string|The name of the image.|image_name|imageName|

### group `az fidalgo image-version`
#### <a name="ImageVersionsListByImage">Command `az fidalgo image-version list`</a>

##### <a name="ExamplesImageVersionsListByImage">Example</a>
```
az fidalgo image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
--resource-group "rg1"
```
##### <a name="ParametersImageVersionsListByImage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--gallery-name**|string|The name of the gallery.|gallery_name|galleryName|
|**--image-name**|string|The name of the image.|image_name|imageName|

#### <a name="ImageVersionsGet">Command `az fidalgo image-version show`</a>

##### <a name="ExamplesImageVersionsGet">Example</a>
```
az fidalgo image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
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

### group `az fidalgo machine-definition`
#### <a name="MachineDefinitionsListByResourceGroup">Command `az fidalgo machine-definition list`</a>

##### <a name="ExamplesMachineDefinitionsListByResourceGroup">Example</a>
```
az fidalgo machine-definition list --resource-group "rg1"
```
##### <a name="ParametersMachineDefinitionsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="MachineDefinitionsListBySubscription">Command `az fidalgo machine-definition list`</a>

##### <a name="ExamplesMachineDefinitionsListBySubscription">Example</a>
```
az fidalgo machine-definition list
```
##### <a name="ParametersMachineDefinitionsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="MachineDefinitionsGet">Command `az fidalgo machine-definition show`</a>

##### <a name="ExamplesMachineDefinitionsGet">Example</a>
```
az fidalgo machine-definition show --name "{machineDefinitionName}" --resource-group "rg1"
```
##### <a name="ParametersMachineDefinitionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--machine-definition-name**|string|The name of the machine definition.|machine_definition_name|machineDefinitionName|

#### <a name="MachineDefinitionsCreateOrUpdate#Create">Command `az fidalgo machine-definition create`</a>

##### <a name="ExamplesMachineDefinitionsCreateOrUpdate#Create">Example</a>
```
az fidalgo machine-definition create --location "centralus" --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c\
9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/exampleImage" --name "{machineDefinitionName}" \
--resource-group "rg1"
```
##### <a name="ParametersMachineDefinitionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--machine-definition-name**|string|The name of the machine definition.|machine_definition_name|machineDefinitionName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--image-reference**|object|Image reference information.|image_reference|imageReference|

#### <a name="MachineDefinitionsUpdate">Command `az fidalgo machine-definition update`</a>

##### <a name="ExamplesMachineDefinitionsUpdate">Example</a>
```
az fidalgo machine-definition update --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceG\
roups/Example/providers/Microsoft.Compute/images/image2" --name "{machineDefinitionName}" --resource-group "rg1"
```
##### <a name="ParametersMachineDefinitionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--machine-definition-name**|string|The name of the machine definition.|machine_definition_name|machineDefinitionName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--image-reference**|object|Image reference information.|image_reference|imageReference|

#### <a name="MachineDefinitionsDelete">Command `az fidalgo machine-definition delete`</a>

##### <a name="ExamplesMachineDefinitionsDelete">Example</a>
```
az fidalgo machine-definition delete --name "{machineDefinitionName}" --resource-group "rg1"
```
##### <a name="ParametersMachineDefinitionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--machine-definition-name**|string|The name of the machine definition.|machine_definition_name|machineDefinitionName|

### group `az fidalgo mapping`
#### <a name="MappingsListByDevCenter">Command `az fidalgo mapping list`</a>

##### <a name="ExamplesMappingsListByDevCenter">Example</a>
```
az fidalgo mapping list --dev-center-name "Contoso" --resource-group "rg1"
```
##### <a name="ParametersMappingsListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="MappingsGet">Command `az fidalgo mapping show`</a>

##### <a name="ExamplesMappingsGet">Example</a>
```
az fidalgo mapping show --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### <a name="ParametersMappingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--mapping-name**|string|Mapping name.|mapping_name|mappingName|

#### <a name="MappingsCreateOrUpdate#Create">Command `az fidalgo mapping create`</a>

##### <a name="ExamplesMappingsCreateOrUpdate#Create">Example</a>
```
az fidalgo mapping create --environment-type "Sandbox" --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a\
-e86e5f9317cc" --project-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/projects/{p\
rojectName}" --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### <a name="ParametersMappingsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--mapping-name**|string|Mapping name.|mapping_name|mappingName|
|**--mapped-subscription-id**|string|Id of a subscription that the environment type will be mapped to. The environment's resources will be deployed into this subscription.|mapped_subscription_id|mappedSubscriptionId|
|**--environment-type**|string|Environment type (e.g. Dev/Test)|environment_type|environmentType|
|**--project-id**|string|Resource Id of a project that this mapping is associated with.|project_id|projectId|

#### <a name="MappingsUpdate">Command `az fidalgo mapping update`</a>

##### <a name="ExamplesMappingsUpdate">Example</a>
```
az fidalgo mapping update --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" \
--dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### <a name="ParametersMappingsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--mapping-name**|string|Mapping name.|mapping_name|mappingName|
|**--mapped-subscription-id**|string|Id of a subscription that the environment type will be mapped to. The environment's resources will be deployed into this subscription.|mapped_subscription_id|mappedSubscriptionId|

#### <a name="MappingsDelete">Command `az fidalgo mapping delete`</a>

##### <a name="ExamplesMappingsDelete">Example</a>
```
az fidalgo mapping delete --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### <a name="ParametersMappingsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--dev-center-name**|string|The name of the devcenter.|dev_center_name|devCenterName|
|**--mapping-name**|string|Mapping name.|mapping_name|mappingName|

### group `az fidalgo network-setting`
#### <a name="NetworkSettingsListByResourceGroup">Command `az fidalgo network-setting list`</a>

##### <a name="ExamplesNetworkSettingsListByResourceGroup">Example</a>
```
az fidalgo network-setting list --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="NetworkSettingsListBySubscription">Command `az fidalgo network-setting list`</a>

##### <a name="ExamplesNetworkSettingsListBySubscription">Example</a>
```
az fidalgo network-setting list
```
##### <a name="ParametersNetworkSettingsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="NetworkSettingsGet">Command `az fidalgo network-setting show`</a>

##### <a name="ExamplesNetworkSettingsGet">Example</a>
```
az fidalgo network-setting show --name "{networkSettingName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|

#### <a name="NetworkSettingsCreateOrUpdate#Create">Command `az fidalgo network-setting create`</a>

##### <a name="ExamplesNetworkSettingsCreateOrUpdate#Create">Example</a>
```
az fidalgo network-setting create --location "centralus" --domain-name "mydomaincontroller.local" --domain-password \
"Password value for user" --domain-username "testuser@mydomaincontroller.local" --networking-resource-group-id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG" --subnet-id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/virtualNetwor\
ks/ExampleVNet/subnets/default" --name "{networkSettingName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--subnet-id**|string|The subnet to attach Virtual Machines to|subnet_id|subnetId|
|**--networking-resource-group-id**|string|Target resource group id for NICs to be placed. Required format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}'|networking_resource_group_id|networkingResourceGroupId|
|**--domain-name**|string|Active Directory domain name|domain_name|domainName|
|**--organization-unit**|string|Active Directory domain Organization Unit (OU)|organization_unit|organizationUnit|
|**--domain-username**|string|The username of an Active Directory account (user or service account) that has permissions to create computer objects in Active Directory. Required format: admin@contoso.com.|domain_username|domainUsername|
|**--domain-password**|string|The password for the account used to join domain|domain_password|domainPassword|

#### <a name="NetworkSettingsUpdate">Command `az fidalgo network-setting update`</a>

##### <a name="ExamplesNetworkSettingsUpdate">Example</a>
```
az fidalgo network-setting update --domain-password "New Password value for user" --name "{networkSettingName}" \
--resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--subnet-id**|string|The subnet to attach Virtual Machines to|subnet_id|subnetId|
|**--networking-resource-group-id**|string|Target resource group id for NICs to be placed. Required format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}'|networking_resource_group_id|networkingResourceGroupId|
|**--domain-name**|string|Active Directory domain name|domain_name|domainName|
|**--organization-unit**|string|Active Directory domain Organization Unit (OU)|organization_unit|organizationUnit|
|**--domain-username**|string|The username of an Active Directory account (user or service account) that has permissions to create computer objects in Active Directory. Required format: admin@contoso.com.|domain_username|domainUsername|
|**--domain-password**|string|The password for the account used to join domain|domain_password|domainPassword|

#### <a name="NetworkSettingsDelete">Command `az fidalgo network-setting delete`</a>

##### <a name="ExamplesNetworkSettingsDelete">Example</a>
```
az fidalgo network-setting delete --name "{networkSettingName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|

#### <a name="NetworkSettingsListHealthDetails">Command `az fidalgo network-setting list-health-detail`</a>

##### <a name="ExamplesNetworkSettingsListHealthDetails">Example</a>
```
az fidalgo network-setting list-health-detail --name "{networkSettingName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsListHealthDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|

#### <a name="NetworkSettingsGetHealthDetails">Command `az fidalgo network-setting show-health-detail`</a>

##### <a name="ExamplesNetworkSettingsGetHealthDetails">Example</a>
```
az fidalgo network-setting show-health-detail --name "{networkSettingName}" --resource-group "rg1"
```
##### <a name="ParametersNetworkSettingsGetHealthDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--network-setting-name**|string|Name of the Network Settings that can be applied to a Pool.|network_setting_name|networkSettingName|

### group `az fidalgo operation-statuses`
#### <a name="OperationStatusesGet">Command `az fidalgo operation-statuses show`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az fidalgo operation-statuses show --operation-id "{operationId}" --location "{location}"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
|**--operation-id**|string|The ID of an ongoing async operation|operation_id|operationId|

### group `az fidalgo pool`
#### <a name="PoolsListByProject">Command `az fidalgo pool list`</a>

##### <a name="ExamplesPoolsListByProject">Example</a>
```
az fidalgo pool list --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="PoolsGet">Command `az fidalgo pool show`</a>

##### <a name="ExamplesPoolsGet">Example</a>
```
az fidalgo pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|

#### <a name="PoolsCreateOrUpdate#Create">Command `az fidalgo pool create`</a>

##### <a name="ExamplesPoolsCreateOrUpdate#Create">Example</a>
```
az fidalgo pool create --location "centralus" --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/r\
g1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" --network-settings-id \
"/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/networksettings/{networkSettingName}" \
--name "medium" --pool-name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--machine-definition-id**|string|Resource Id of a Machine Definition|machine_definition_id|machineDefinitionId|
|**--network-settings-id**|string|Resource Id of a Network Settings resource|network_settings_id|networkSettingsId|
|**--name**|string|The name of the SKU.|name|name|

#### <a name="PoolsUpdate">Command `az fidalgo pool update`</a>

##### <a name="ExamplesPoolsUpdate">Example</a>
```
az fidalgo pool update --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.\
Fidalgo/machinedefinitions/{machineDefinitionName}" --pool-name "{poolName}" --project-name "{projectName}" \
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
|**--machine-definition-id**|string|Resource Id of a Machine Definition|machine_definition_id|machineDefinitionId|
|**--network-settings-id**|string|Resource Id of a Network Settings resource|network_settings_id|networkSettingsId|
|**--name**|string|The name of the SKU.|name|name|

#### <a name="PoolsDelete">Command `az fidalgo pool delete`</a>

##### <a name="ExamplesPoolsDelete">Example</a>
```
az fidalgo pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|
|**--pool-name**|string|Name of the pool.|pool_name|poolName|

### group `az fidalgo project`
#### <a name="ProjectsListByResourceGroup">Command `az fidalgo project list`</a>

##### <a name="ExamplesProjectsListByResourceGroup">Example</a>
```
az fidalgo project list --resource-group "rg1"
```
##### <a name="ParametersProjectsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ProjectsListBySubscription">Command `az fidalgo project list`</a>

##### <a name="ExamplesProjectsListBySubscription">Example</a>
```
az fidalgo project list
```
##### <a name="ParametersProjectsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|

#### <a name="ProjectsGet">Command `az fidalgo project show`</a>

##### <a name="ExamplesProjectsGet">Example</a>
```
az fidalgo project show --name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersProjectsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|

#### <a name="ProjectsCreateOrUpdate#Create">Command `az fidalgo project create`</a>

##### <a name="ExamplesProjectsCreateOrUpdate#Create">Example</a>
```
az fidalgo project create --location "centralus" --description "This is my first project." --dev-center-id \
"/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/devcenters/{devCenterName}" --tags \
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

#### <a name="ProjectsUpdate">Command `az fidalgo project update`</a>

##### <a name="ExamplesProjectsUpdate">Example</a>
```
az fidalgo project update --description "This is my first project." --tags CostCenter="R&D" --name "{projectName}" \
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

#### <a name="ProjectsDelete">Command `az fidalgo project delete`</a>

##### <a name="ExamplesProjectsDelete">Example</a>
```
az fidalgo project delete --name "{projectName}" --resource-group "rg1"
```
##### <a name="ParametersProjectsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--project-name**|string|The name of the project.|project_name|projectName|

### group `az fidalgo sku`
#### <a name="SkusListBySubscription">Command `az fidalgo sku list`</a>

##### <a name="ExamplesSkusListBySubscription">Example</a>
```
az fidalgo sku list
```
##### <a name="ParametersSkusListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: '$top=10'.|top|$top|
