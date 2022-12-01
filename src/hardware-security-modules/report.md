# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az hardware-security-modules|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az hardware-security-modules` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az hardware-security-modules dedicated-hsm|DedicatedHsm|[commands](#CommandsInDedicatedHsm)|

## COMMANDS
### <a name="CommandsInDedicatedHsm">Commands in `az hardware-security-modules dedicated-hsm` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az hardware-security-modules dedicated-hsm list](#DedicatedHsmListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDedicatedHsmListByResourceGroup)|[Example](#ExamplesDedicatedHsmListByResourceGroup)|
|[az hardware-security-modules dedicated-hsm list](#DedicatedHsmListBySubscription)|ListBySubscription|[Parameters](#ParametersDedicatedHsmListBySubscription)|[Example](#ExamplesDedicatedHsmListBySubscription)|
|[az hardware-security-modules dedicated-hsm show](#DedicatedHsmGet)|Get|[Parameters](#ParametersDedicatedHsmGet)|[Example](#ExamplesDedicatedHsmGet)|
|[az hardware-security-modules dedicated-hsm create](#DedicatedHsmCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDedicatedHsmCreateOrUpdate#Create)|[Example](#ExamplesDedicatedHsmCreateOrUpdate#Create)|
|[az hardware-security-modules dedicated-hsm update](#DedicatedHsmUpdate)|Update|[Parameters](#ParametersDedicatedHsmUpdate)|[Example](#ExamplesDedicatedHsmUpdate)|
|[az hardware-security-modules dedicated-hsm delete](#DedicatedHsmDelete)|Delete|[Parameters](#ParametersDedicatedHsmDelete)|[Example](#ExamplesDedicatedHsmDelete)|
|[az hardware-security-modules dedicated-hsm list-outbound-network-dependency-endpoint](#DedicatedHsmListOutboundNetworkDependenciesEndpoints)|ListOutboundNetworkDependenciesEndpoints|[Parameters](#ParametersDedicatedHsmListOutboundNetworkDependenciesEndpoints)|[Example](#ExamplesDedicatedHsmListOutboundNetworkDependenciesEndpoints)|


## COMMAND DETAILS
### group `az hardware-security-modules dedicated-hsm`
#### <a name="DedicatedHsmListByResourceGroup">Command `az hardware-security-modules dedicated-hsm list`</a>

##### <a name="ExamplesDedicatedHsmListByResourceGroup">Example</a>
```
az hardware-security-modules dedicated-hsm list --resource-group "hsm-group"
az hardware-security-modules dedicated-hsm list --resource-group "hsm-group"
```
##### <a name="ParametersDedicatedHsmListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|resourceGroupName|
|**--top**|integer|Maximum number of results to return.|top|$top|

#### <a name="DedicatedHsmListBySubscription">Command `az hardware-security-modules dedicated-hsm list`</a>

##### <a name="ExamplesDedicatedHsmListBySubscription">Example</a>
```
az hardware-security-modules dedicated-hsm list
az hardware-security-modules dedicated-hsm list
```
##### <a name="ParametersDedicatedHsmListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|Maximum number of results to return.|top|$top|

#### <a name="DedicatedHsmGet">Command `az hardware-security-modules dedicated-hsm show`</a>

##### <a name="ExamplesDedicatedHsmGet">Example</a>
```
az hardware-security-modules dedicated-hsm show --name "hsm1" --resource-group "hsm-group"
az hardware-security-modules dedicated-hsm show --name "hsm1" --resource-group "hsm-group"
az hardware-security-modules dedicated-hsm show --name "hsm1" --resource-group "hsm-group"
```
##### <a name="ParametersDedicatedHsmGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated hsm belongs.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the dedicated HSM.|name|name|

#### <a name="DedicatedHsmCreateOrUpdate#Create">Command `az hardware-security-modules dedicated-hsm create`</a>

##### <a name="ExamplesDedicatedHsmCreateOrUpdate#Create">Example</a>
```
az hardware-security-modules dedicated-hsm create --name "hsm1" --location "westus" --network-profile-network-interface\
s private-ip-address="1.0.0.1" --api-entity-reference-subnet id="/subscriptions/00000000-0000-0000-0000-000000000000/re\
sourceGroups/hsm-group/providers/Microsoft.Network/virtualNetworks/stamp01/subnets/stamp01" --stamp-id "stamp01" \
--sku-name "SafeNet Luna Network HSM A790" --tags Dept="hsm" Environment="dogfood" --resource-group "hsm-group"
az hardware-security-modules dedicated-hsm create --name "hsm1" --location "westus" --network-profile-network-interface\
s private-ip-address="1.0.0.1" --api-entity-reference-subnet id="/subscriptions/00000000-0000-0000-0000-000000000000/re\
sourceGroups/hsm-group/providers/Microsoft.Network/virtualNetworks/stamp01/subnets/stamp01" --stamp-id "stamp01" \
--sku-name "payShield10K_LMK1_CPS60" --tags Dept="hsm" Environment="dogfood" --resource-group "hsm-group"
az hardware-security-modules dedicated-hsm create --name "hsm1" --location "westus" --network-interfaces \
private-ip-address="1.0.0.2" --subnet id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/hsm-group/\
providers/Microsoft.Network/virtualNetworks/stamp01/subnets/stamp01" --network-profile-network-interfaces \
private-ip-address="1.0.0.1" --api-entity-reference-subnet id="/subscriptions/00000000-0000-0000-0000-000000000000/reso\
urceGroups/hsm-group/providers/Microsoft.Network/virtualNetworks/stamp01/subnets/stamp01" --stamp-id "stamp01" \
--sku-name "payShield10K_LMK1_CPS60" --tags Dept="hsm" Environment="dogfood" --resource-group "hsm-group"
```
##### <a name="ParametersDedicatedHsmCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the resource belongs.|resource_group_name|resourceGroupName|
|**--name**|string|Name of the dedicated Hsm|name|name|
|**--location**|string|The supported Azure location where the dedicated HSM should be created.|location|location|
|**--zones**|array|The Dedicated Hsm zones.|zones|zones|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--sku-name**|choice|SKU of the dedicated HSM|sku_name|name|
|**--stamp-id**|string|This field will be used when RP does not support Availability zones.|stamp_id|stampId|
|**--subnet**|object|Specifies the identifier of the subnet.|subnet|subnet|
|**--network-interfaces**|array|Specifies the list of resource Ids for the network interfaces associated with the dedicated HSM.|network_interfaces|networkInterfaces|
|**--api-entity-reference-subnet**|object|Specifies the identifier of the subnet.|api_entity_reference_subnet|subnet|
|**--network-profile-network-interfaces**|array|Specifies the list of resource Ids for the network interfaces associated with the dedicated HSM.|network_profile_network_interfaces|networkInterfaces|

#### <a name="DedicatedHsmUpdate">Command `az hardware-security-modules dedicated-hsm update`</a>

##### <a name="ExamplesDedicatedHsmUpdate">Example</a>
```
az hardware-security-modules dedicated-hsm update --name "hsm1" --tags Dept="hsm" Environment="dogfood" Slice="A" \
--resource-group "hsm-group"
az hardware-security-modules dedicated-hsm update --name "hsm1" --tags Dept="hsm" Environment="dogfood" Slice="A" \
--resource-group "hsm-group"
```
##### <a name="ParametersDedicatedHsmUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the server belongs.|resource_group_name|resourceGroupName|
|**--name**|string|Name of the dedicated HSM|name|name|
|**--tags**|dictionary|Resource tags|tags|tags|

#### <a name="DedicatedHsmDelete">Command `az hardware-security-modules dedicated-hsm delete`</a>

##### <a name="ExamplesDedicatedHsmDelete">Example</a>
```
az hardware-security-modules dedicated-hsm delete --name "hsm1" --resource-group "hsm-group"
```
##### <a name="ParametersDedicatedHsmDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the dedicated HSM to delete|name|name|

#### <a name="DedicatedHsmListOutboundNetworkDependenciesEndpoints">Command `az hardware-security-modules dedicated-hsm list-outbound-network-dependency-endpoint`</a>

##### <a name="ExamplesDedicatedHsmListOutboundNetworkDependenciesEndpoints">Example</a>
```
az hardware-security-modules dedicated-hsm list-outbound-network-dependency-endpoint --name "hsm1" --resource-group \
"hsm-group"
```
##### <a name="ParametersDedicatedHsmListOutboundNetworkDependenciesEndpoints">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated hsm belongs.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the dedicated HSM.|name|name|
