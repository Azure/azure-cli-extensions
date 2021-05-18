# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az windows-iot-services|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az windows-iot-services` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az windows-iot-services|Services|[commands](#CommandsInServices)|

## COMMANDS
### <a name="CommandsInServices">Commands in `az windows-iot-services` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az windows-iot-services list](#ServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersServicesListByResourceGroup)|[Example](#ExamplesServicesListByResourceGroup)|
|[az windows-iot-services list](#ServicesList)|List|[Parameters](#ParametersServicesList)|[Example](#ExamplesServicesList)|
|[az windows-iot-services show](#ServicesGet)|Get|[Parameters](#ParametersServicesGet)|[Example](#ExamplesServicesGet)|
|[az windows-iot-services create](#ServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersServicesCreateOrUpdate#Create)|[Example](#ExamplesServicesCreateOrUpdate#Create)|
|[az windows-iot-services update](#ServicesUpdate)|Update|[Parameters](#ParametersServicesUpdate)|[Example](#ExamplesServicesUpdate)|
|[az windows-iot-services delete](#ServicesDelete)|Delete|[Parameters](#ParametersServicesDelete)|[Example](#ExamplesServicesDelete)|


## COMMAND DETAILS

### group `az windows-iot-services`
#### <a name="ServicesListByResourceGroup">Command `az windows-iot-services list`</a>

##### <a name="ExamplesServicesListByResourceGroup">Example</a>
```
az windows-iot-services list --resource-group "res6117"
```
##### <a name="ParametersServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|

#### <a name="ServicesList">Command `az windows-iot-services list`</a>

##### <a name="ExamplesServicesList">Example</a>
```
az windows-iot-services list
```
##### <a name="ParametersServicesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ServicesGet">Command `az windows-iot-services show`</a>

##### <a name="ExamplesServicesGet">Example</a>
```
az windows-iot-services show --name "service8596" --resource-group "res9407"
```
##### <a name="ParametersServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|

#### <a name="ServicesCreateOrUpdate#Create">Command `az windows-iot-services create`</a>

##### <a name="ExamplesServicesCreateOrUpdate#Create">Example</a>
```
az windows-iot-services create --name "service4445" --location "East US" --admin-domain-name "d.e.f" \
--billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9101"
```
##### <a name="ParametersServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--location**|string|The Azure Region where the resource lives|location|location|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation.|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|

#### <a name="ServicesUpdate">Command `az windows-iot-services update`</a>

##### <a name="ExamplesServicesUpdate">Example</a>
```
az windows-iot-services update --name "service8596" --admin-domain-name "d.e.f" --billing-domain-name "a.b.c" --notes \
"blah" --quantity 1000000 --resource-group "res9407"
```
##### <a name="ParametersServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation.|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|

#### <a name="ServicesDelete">Command `az windows-iot-services delete`</a>

##### <a name="ExamplesServicesDelete">Example</a>
```
az windows-iot-services delete --name "service2434" --resource-group "res4228"
```
##### <a name="ParametersServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
