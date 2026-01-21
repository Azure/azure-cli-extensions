# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az adb2c|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az adb2c` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az adb2c tenant|B2CTenants|[commands](#CommandsInB2CTenants)|

## COMMANDS
### <a name="CommandsInB2CTenants">Commands in `az adb2c tenant` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az adb2c tenant list](#B2CTenantsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersB2CTenantsListByResourceGroup)|[Example](#ExamplesB2CTenantsListByResourceGroup)|
|[az adb2c tenant list](#B2CTenantsListBySubscription)|ListBySubscription|[Parameters](#ParametersB2CTenantsListBySubscription)|[Example](#ExamplesB2CTenantsListBySubscription)|
|[az adb2c tenant show](#B2CTenantsGet)|Get|[Parameters](#ParametersB2CTenantsGet)|[Example](#ExamplesB2CTenantsGet)|
|[az adb2c tenant create](#B2CTenantsCreate)|Create|[Parameters](#ParametersB2CTenantsCreate)|[Example](#ExamplesB2CTenantsCreate)|
|[az adb2c tenant update](#B2CTenantsUpdate)|Update|[Parameters](#ParametersB2CTenantsUpdate)|[Example](#ExamplesB2CTenantsUpdate)|
|[az adb2c tenant delete](#B2CTenantsDelete)|Delete|[Parameters](#ParametersB2CTenantsDelete)|[Example](#ExamplesB2CTenantsDelete)|


## COMMAND DETAILS

### group `az adb2c tenant`
#### <a name="B2CTenantsListByResourceGroup">Command `az adb2c tenant list`</a>

##### <a name="ExamplesB2CTenantsListByResourceGroup">Example</a>
```
az adb2c tenant list --resource-group "contosoResourceGroup"
```
##### <a name="ParametersB2CTenantsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

#### <a name="B2CTenantsListBySubscription">Command `az adb2c tenant list`</a>

##### <a name="ExamplesB2CTenantsListBySubscription">Example</a>
```
az adb2c tenant list
```
##### <a name="ParametersB2CTenantsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="B2CTenantsGet">Command `az adb2c tenant show`</a>

##### <a name="ExamplesB2CTenantsGet">Example</a>
```
az adb2c tenant show --resource-group "contosoResourceGroup" --name "contoso.onmicrosoft.com"
```
##### <a name="ParametersB2CTenantsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The initial domain name of the B2C tenant.|resource_name|resourceName|

#### <a name="B2CTenantsCreate">Command `az adb2c tenant create`</a>

##### <a name="ExamplesB2CTenantsCreate">Example</a>
```
az adb2c tenant create --location "United States" --country-code "US" --display-name "Contoso" --sku "Standard" \
--resource-group "contosoResourceGroup" --name "contoso.onmicrosoft.com"
```
##### <a name="ParametersB2CTenantsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The initial domain name of the B2C tenant.|resource_name|resourceName|
|**--location**|string|The location in which the resource is hosted and data resides. Refer to [this documentation](https://aka.ms/B2CDataResidency) to see valid data residency locations. Please choose one of 'United States', 'Europe', and 'Asia Pacific'.|location|location|
|**--tags**|dictionary|Resource Tags|tags|tags|
|**--name**|sealed-choice|The name of the SKU for the tenant.|name|name|
|**--display-name**|string|The display name of the B2C tenant.|display_name|displayName|
|**--country-code**|string|Country code of Azure tenant (e.g. 'US'). Refer to [aka.ms/B2CDataResidency](https://aka.ms/B2CDataResidency) to see valid country codes and corresponding data residency locations. If you do not see a country code in an valid data residency location, choose one from the list.|country_code|countryCode|

#### <a name="B2CTenantsUpdate">Command `az adb2c tenant update`</a>

##### <a name="ExamplesB2CTenantsUpdate">Example</a>
```
az adb2c tenant update --resource-group "contosoResourceGroup" --name "contoso.onmicrosoft.com" --billing-type "MAU" \
--sku "PremiumP1" --tags key="value"
```
##### <a name="ParametersB2CTenantsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The initial domain name of the B2C tenant.|resource_name|resourceName|
|**--tags**|dictionary|Resource Tags|tags|tags|
|**--billing-type**|sealed-choice|The type of billing. Will be MAU for all new customers. If 'Auths', it can be updated to 'MAU'. Cannot be changed if value is 'MAU'. Learn more about Azure AD B2C billing at [aka.ms/b2cBilling](https://aka.ms/b2cbilling).|billing_type|billingType|
|**--name**|sealed-choice|The name of the SKU for the tenant.|name|name|

#### <a name="B2CTenantsDelete">Command `az adb2c tenant delete`</a>

##### <a name="ExamplesB2CTenantsDelete">Example</a>
```
az adb2c tenant delete --resource-group "rg1" --name "contoso.onmicrosoft.com"
```
##### <a name="ParametersB2CTenantsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The initial domain name of the B2C tenant.|resource_name|resourceName|
