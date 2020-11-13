# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az portal|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az portal` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az portal dashboard|Dashboards|[commands](#CommandsInDashboards)|
|az portal tenant-configuration|TenantConfigurations|[commands](#CommandsInTenantConfigurations)|
|az portal list-tenant-configuration-violation|ListTenantConfigurationViolations|[commands](#CommandsInListTenantConfigurationViolations)|

## COMMANDS
### <a name="CommandsInDashboards">Commands in `az portal dashboard` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az portal dashboard list](#DashboardsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDashboardsListByResourceGroup)|[Example](#ExamplesDashboardsListByResourceGroup)|
|[az portal dashboard list](#DashboardsListBySubscription)|ListBySubscription|[Parameters](#ParametersDashboardsListBySubscription)|[Example](#ExamplesDashboardsListBySubscription)|
|[az portal dashboard show](#DashboardsGet)|Get|[Parameters](#ParametersDashboardsGet)|[Example](#ExamplesDashboardsGet)|
|[az portal dashboard create](#DashboardsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDashboardsCreateOrUpdate#Create)|[Example](#ExamplesDashboardsCreateOrUpdate#Create)|
|[az portal dashboard update](#DashboardsUpdate)|Update|[Parameters](#ParametersDashboardsUpdate)|[Example](#ExamplesDashboardsUpdate)|
|[az portal dashboard delete](#DashboardsDelete)|Delete|[Parameters](#ParametersDashboardsDelete)|[Example](#ExamplesDashboardsDelete)|

### <a name="CommandsInListTenantConfigurationViolations">Commands in `az portal list-tenant-configuration-violation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az portal list-tenant-configuration-violation list](#ListTenantConfigurationViolationsList)|List|[Parameters](#ParametersListTenantConfigurationViolationsList)|[Example](#ExamplesListTenantConfigurationViolationsList)|

### <a name="CommandsInTenantConfigurations">Commands in `az portal tenant-configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az portal tenant-configuration list](#TenantConfigurationsList)|List|[Parameters](#ParametersTenantConfigurationsList)|[Example](#ExamplesTenantConfigurationsList)|
|[az portal tenant-configuration show](#TenantConfigurationsGet)|Get|[Parameters](#ParametersTenantConfigurationsGet)|[Example](#ExamplesTenantConfigurationsGet)|
|[az portal tenant-configuration create](#TenantConfigurationsCreate)|Create|[Parameters](#ParametersTenantConfigurationsCreate)|[Example](#ExamplesTenantConfigurationsCreate)|
|[az portal tenant-configuration delete](#TenantConfigurationsDelete)|Delete|[Parameters](#ParametersTenantConfigurationsDelete)|[Example](#ExamplesTenantConfigurationsDelete)|


## COMMAND DETAILS

### group `az portal dashboard`
#### <a name="DashboardsListByResourceGroup">Command `az portal dashboard list`</a>

##### <a name="ExamplesDashboardsListByResourceGroup">Example</a>
```
az portal dashboard list --resource-group "testRG"
```
##### <a name="ParametersDashboardsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

#### <a name="DashboardsListBySubscription">Command `az portal dashboard list`</a>

##### <a name="ExamplesDashboardsListBySubscription">Example</a>
```
az portal dashboard list
```
##### <a name="ParametersDashboardsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DashboardsGet">Command `az portal dashboard show`</a>

##### <a name="ExamplesDashboardsGet">Example</a>
```
az portal dashboard show --name "testDashboard" --resource-group "testRG"
```
##### <a name="ParametersDashboardsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|

#### <a name="DashboardsCreateOrUpdate#Create">Command `az portal dashboard create`</a>

##### <a name="ExamplesDashboardsCreateOrUpdate#Create">Example</a>
```
az portal dashboard create --location "eastus" --lenses "[{\\"order\\":1,\\"parts\\":[{\\"position\\":{\\"colSpan\\":3,\
\\"rowSpan\\":4,\\"x\\":1,\\"y\\":2}},{\\"position\\":{\\"colSpan\\":6,\\"rowSpan\\":6,\\"x\\":5,\\"y\\":5}}]},{\\"orde\
r\\":2,\\"parts\\":[]}]" --metadata "{\\"metadata\\":{\\"ColSpan\\":2,\\"RowSpan\\":1,\\"X\\":4,\\"Y\\":3}}" --tags \
aKey="aValue" anotherKey="anotherValue" --name "testDashboard" --resource-group "testRG"
```
##### <a name="ParametersDashboardsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--lenses**|array|The dashboard lenses.|lenses|lenses|
|**--metadata**|dictionary|The dashboard metadata.|metadata|metadata|

#### <a name="DashboardsUpdate">Command `az portal dashboard update`</a>

##### <a name="ExamplesDashboardsUpdate">Example</a>
```
az portal dashboard update --tags aKey="bValue" anotherKey="anotherValue2" --name "testDashboard" --resource-group \
"testRG"
```
##### <a name="ParametersDashboardsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--lenses**|array|The dashboard lenses.|lenses|lenses|
|**--metadata**|dictionary|The dashboard metadata.|metadata|metadata|

#### <a name="DashboardsDelete">Command `az portal dashboard delete`</a>

##### <a name="ExamplesDashboardsDelete">Example</a>
```
az portal dashboard delete --name "testDashboard" --resource-group "testRG"
```
##### <a name="ParametersDashboardsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|

### group `az portal list-tenant-configuration-violation`
#### <a name="ListTenantConfigurationViolationsList">Command `az portal list-tenant-configuration-violation list`</a>

##### <a name="ExamplesListTenantConfigurationViolationsList">Example</a>
```
az portal list-tenant-configuration-violation list
```
##### <a name="ParametersListTenantConfigurationViolationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az portal tenant-configuration`
#### <a name="TenantConfigurationsList">Command `az portal tenant-configuration list`</a>

##### <a name="ExamplesTenantConfigurationsList">Example</a>
```
az portal tenant-configuration list
```
##### <a name="ParametersTenantConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="TenantConfigurationsGet">Command `az portal tenant-configuration show`</a>

##### <a name="ExamplesTenantConfigurationsGet">Example</a>
```
az portal tenant-configuration show
```
##### <a name="ParametersTenantConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="TenantConfigurationsCreate">Command `az portal tenant-configuration create`</a>

##### <a name="ExamplesTenantConfigurationsCreate">Example</a>
```
az portal tenant-configuration create --enforce-private-markdown-storage true
```
##### <a name="ParametersTenantConfigurationsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--enforce-private-markdown-storage**|boolean|When flag is set to true Markdown tile will require external storage configuration (URI). The inline content configuration will be prohibited.|enforce_private_markdown_storage|enforcePrivateMarkdownStorage|

#### <a name="TenantConfigurationsDelete">Command `az portal tenant-configuration delete`</a>

##### <a name="ExamplesTenantConfigurationsDelete">Example</a>
```
az portal tenant-configuration delete
```
##### <a name="ParametersTenantConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|