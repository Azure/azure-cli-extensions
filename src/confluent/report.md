# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az confluent|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az confluent` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az confluent terms|MarketplaceAgreements|[commands](#CommandsInMarketplaceAgreements)|
|az confluent organization|Organization|[commands](#CommandsInOrganization)|

## COMMANDS
### <a name="CommandsInOrganization">Commands in `az confluent organization` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az confluent organization list](#OrganizationListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersOrganizationListByResourceGroup)|[Example](#ExamplesOrganizationListByResourceGroup)|
|[az confluent organization list](#OrganizationListBySubscription)|ListBySubscription|[Parameters](#ParametersOrganizationListBySubscription)|[Example](#ExamplesOrganizationListBySubscription)|
|[az confluent organization show](#OrganizationGet)|Get|[Parameters](#ParametersOrganizationGet)|[Example](#ExamplesOrganizationGet)|
|[az confluent organization create](#OrganizationCreate)|Create|[Parameters](#ParametersOrganizationCreate)|[Example](#ExamplesOrganizationCreate)|
|[az confluent organization update](#OrganizationUpdate)|Update|[Parameters](#ParametersOrganizationUpdate)|[Example](#ExamplesOrganizationUpdate)|
|[az confluent organization delete](#OrganizationDelete)|Delete|[Parameters](#ParametersOrganizationDelete)|[Example](#ExamplesOrganizationDelete)|

### <a name="CommandsInMarketplaceAgreements">Commands in `az confluent terms` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az confluent terms list](#MarketplaceAgreementsList)|List|[Parameters](#ParametersMarketplaceAgreementsList)|[Example](#ExamplesMarketplaceAgreementsList)|


## COMMAND DETAILS

### group `az confluent organization`
#### <a name="OrganizationListByResourceGroup">Command `az confluent organization list`</a>

##### <a name="ExamplesOrganizationListByResourceGroup">Example</a>
```
az confluent organization list --resource-group "myResourceGroup"
```
##### <a name="ParametersOrganizationListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|

#### <a name="OrganizationListBySubscription">Command `az confluent organization list`</a>

##### <a name="ExamplesOrganizationListBySubscription">Example</a>
```
az confluent organization list
```
##### <a name="ParametersOrganizationListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="OrganizationGet">Command `az confluent organization show`</a>

##### <a name="ExamplesOrganizationGet">Example</a>
```
az confluent organization show --name "myOrganization" --resource-group "myResourceGroup"
```
##### <a name="ParametersOrganizationGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--organization-name**|string|Organization resource name|organization_name|organizationName|

#### <a name="OrganizationCreate">Command `az confluent organization create`</a>

##### <a name="ExamplesOrganizationCreate">Example</a>
```
az confluent organization create --location "West US" --tags Environment="Dev" --name "myOrganization" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersOrganizationCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--organization-name**|string|Organization resource name|organization_name|organizationName|
|**--tags**|dictionary|Organization resource tags|tags|tags|
|**--location**|string|Location of Organization resource|location|location|
|**--publisher-id**|string|Publisher Id|publisher_id|publisherId|
|**--offer-id**|string|Offer Id|offer_id|id|
|**--plan-id**|string|Offer Plan Id|plan_id|planId|
|**--plan-name**|string|Offer Plan Name|plan_name|planName|
|**--term-unit**|string|Offer Plan Term unit|term_unit|termUnit|

#### <a name="OrganizationUpdate">Command `az confluent organization update`</a>

##### <a name="ExamplesOrganizationUpdate">Example</a>
```
az confluent organization update --tags client="dev-client" env="dev" --name "myOrganization" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersOrganizationUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--organization-name**|string|Organization resource name|organization_name|organizationName|
|**--tags**|dictionary|ARM resource tags|tags|tags|

#### <a name="OrganizationDelete">Command `az confluent organization delete`</a>

##### <a name="ExamplesOrganizationDelete">Example</a>
```
az confluent organization delete --name "myOrganization" --resource-group "myResourceGroup"
```
##### <a name="ParametersOrganizationDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--organization-name**|string|Organization resource name|organization_name|organizationName|

### group `az confluent terms`
#### <a name="MarketplaceAgreementsList">Command `az confluent terms list`</a>

##### <a name="ExamplesMarketplaceAgreementsList">Example</a>
```
az confluent terms list
```
##### <a name="ParametersMarketplaceAgreementsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|