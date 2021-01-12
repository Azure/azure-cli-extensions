# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az windowsiotservices|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az windowsiotservices` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az windowsiotservices service|Services|[commands](#CommandsInServices)|

## COMMANDS
### <a name="CommandsInServices">Commands in `az windowsiotservices service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az windowsiotservices service list](#ServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersServicesListByResourceGroup)|[Example](#ExamplesServicesListByResourceGroup)|
|[az windowsiotservices service list](#ServicesList)|List|[Parameters](#ParametersServicesList)|[Example](#ExamplesServicesList)|
|[az windowsiotservices service show](#ServicesGet)|Get|[Parameters](#ParametersServicesGet)|[Example](#ExamplesServicesGet)|
|[az windowsiotservices service create](#ServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersServicesCreateOrUpdate#Create)|[Example](#ExamplesServicesCreateOrUpdate#Create)|
|[az windowsiotservices service update](#ServicesUpdate)|Update|[Parameters](#ParametersServicesUpdate)|[Example](#ExamplesServicesUpdate)|
|[az windowsiotservices service delete](#ServicesDelete)|Delete|[Parameters](#ParametersServicesDelete)|[Example](#ExamplesServicesDelete)|
|[az windowsiotservices service check-device-service-name-availability](#ServicesCheckDeviceServiceNameAvailability)|CheckDeviceServiceNameAvailability|[Parameters](#ParametersServicesCheckDeviceServiceNameAvailability)|[Example](#ExamplesServicesCheckDeviceServiceNameAvailability)|


## COMMAND DETAILS

### group `az windowsiotservices service`
#### <a name="ServicesListByResourceGroup">Command `az windowsiotservices service list`</a>

##### <a name="ExamplesServicesListByResourceGroup">Example</a>
```
az windowsiotservices service list --resource-group "res6117"
```
##### <a name="ParametersServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|

#### <a name="ServicesList">Command `az windowsiotservices service list`</a>

##### <a name="ExamplesServicesList">Example</a>
```
az windowsiotservices service list
```
##### <a name="ParametersServicesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ServicesGet">Command `az windowsiotservices service show`</a>

##### <a name="ExamplesServicesGet">Example</a>
```
az windowsiotservices service show --device-name "service8596" --resource-group "res9407"
```
##### <a name="ParametersServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|

#### <a name="ServicesCreateOrUpdate#Create">Command `az windowsiotservices service create`</a>

##### <a name="ExamplesServicesCreateOrUpdate#Create">Example</a>
```
az windowsiotservices service create --device-name "service4445" --location "East US" --admin-domain-name "d.e.f" \
--billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9101"
```
##### <a name="ParametersServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--if-match**|string|ETag of the Windows IoT Device Service. Do not specify for creating a new Windows IoT Device Service. Required to update an existing Windows IoT Device Service.|if_match|If-Match|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The Azure Region where the resource lives|location|location|
|**--etag**|string|The Etag field is *not* required. If it is provided in the response body, it must also be provided as a header per the normal ETag convention.|etag|etag|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation,|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|

#### <a name="ServicesUpdate">Command `az windowsiotservices service update`</a>

##### <a name="ExamplesServicesUpdate">Example</a>
```
az windowsiotservices service update --device-name "service8596" --location "East US" --admin-domain-name "d.e.f" \
--billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9407"
```
##### <a name="ParametersServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--if-match**|string|ETag of the Windows IoT Device Service. Do not specify for creating a brand new Windows IoT Device Service. Required to update an existing Windows IoT Device Service.|if_match|If-Match|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The Azure Region where the resource lives|location|location|
|**--etag**|string|The Etag field is *not* required. If it is provided in the response body, it must also be provided as a header per the normal ETag convention.|etag|etag|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation,|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|

#### <a name="ServicesDelete">Command `az windowsiotservices service delete`</a>

##### <a name="ExamplesServicesDelete">Example</a>
```
az windowsiotservices service delete --device-name "service2434" --resource-group "res4228"
```
##### <a name="ParametersServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|

#### <a name="ServicesCheckDeviceServiceNameAvailability">Command `az windowsiotservices service check-device-service-name-availability`</a>

##### <a name="ExamplesServicesCheckDeviceServiceNameAvailability">Example</a>
```
az windowsiotservices service check-device-service-name-availability --name "service3363"
```
##### <a name="ParametersServicesCheckDeviceServiceNameAvailability">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the Windows IoT Device Service to check.|name|name|
