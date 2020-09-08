# Azure CLI Module Creation Report

### portal dashboard create

create a portal dashboard.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal dashboard|Dashboards|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--lenses**|dictionary|The dashboard lenses.|lenses|lenses|
|**--metadata**|dictionary|The dashboard metadata.|metadata|metadata|

### portal dashboard delete

delete a portal dashboard.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal dashboard|Dashboards|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|

### portal dashboard list

list a portal dashboard.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal dashboard|Dashboards|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

### portal dashboard show

show a portal dashboard.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal dashboard|Dashboards|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|

### portal dashboard update

update a portal dashboard.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal dashboard|Dashboards|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--dashboard-name**|string|The name of the dashboard.|dashboard_name|dashboardName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--lenses**|dictionary|The dashboard lenses.|lenses|lenses|
|**--metadata**|dictionary|The dashboard metadata.|metadata|metadata|

### portal tenant-configuration create

create a portal tenant-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal tenant-configuration|TenantConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--enforce-private-markdown-storage**|boolean|When flag is set to true Markdown tile will require external storage configuration (URI). The inline content configuration will be prohibited.|enforce_private_markdown_storage|enforcePrivateMarkdownStorage|

### portal tenant-configuration delete

delete a portal tenant-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal tenant-configuration|TenantConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### portal tenant-configuration list

list a portal tenant-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal tenant-configuration|TenantConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### portal tenant-configuration show

show a portal tenant-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|portal tenant-configuration|TenantConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
