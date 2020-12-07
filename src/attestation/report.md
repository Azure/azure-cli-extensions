# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az attestation|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az attestation` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az attestation attestation-provider|AttestationProviders|[commands](#CommandsInAttestationProviders)|

## COMMANDS
### <a name="CommandsInAttestationProviders">Commands in `az attestation attestation-provider` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az attestation attestation-provider list](#AttestationProvidersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersAttestationProvidersListByResourceGroup)|[Example](#ExamplesAttestationProvidersListByResourceGroup)|
|[az attestation attestation-provider list](#AttestationProvidersList)|List|[Parameters](#ParametersAttestationProvidersList)|[Example](#ExamplesAttestationProvidersList)|
|[az attestation attestation-provider show](#AttestationProvidersGet)|Get|[Parameters](#ParametersAttestationProvidersGet)|[Example](#ExamplesAttestationProvidersGet)|
|[az attestation attestation-provider create](#AttestationProvidersCreate)|Create|[Parameters](#ParametersAttestationProvidersCreate)|[Example](#ExamplesAttestationProvidersCreate)|
|[az attestation attestation-provider update](#AttestationProvidersUpdate)|Update|[Parameters](#ParametersAttestationProvidersUpdate)|[Example](#ExamplesAttestationProvidersUpdate)|
|[az attestation attestation-provider delete](#AttestationProvidersDelete)|Delete|[Parameters](#ParametersAttestationProvidersDelete)|[Example](#ExamplesAttestationProvidersDelete)|
|[az attestation attestation-provider get-default-by-location](#AttestationProvidersGetDefaultByLocation)|GetDefaultByLocation|[Parameters](#ParametersAttestationProvidersGetDefaultByLocation)|[Example](#ExamplesAttestationProvidersGetDefaultByLocation)|
|[az attestation attestation-provider list-default](#AttestationProvidersListDefault)|ListDefault|[Parameters](#ParametersAttestationProvidersListDefault)|[Example](#ExamplesAttestationProvidersListDefault)|


## COMMAND DETAILS

### group `az attestation attestation-provider`
#### <a name="AttestationProvidersListByResourceGroup">Command `az attestation attestation-provider list`</a>

##### <a name="ExamplesAttestationProvidersListByResourceGroup">Example</a>
```
az attestation attestation-provider list --resource-group "testrg1"
```
##### <a name="ParametersAttestationProvidersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="AttestationProvidersList">Command `az attestation attestation-provider list`</a>

##### <a name="ExamplesAttestationProvidersList">Example</a>
```
az attestation attestation-provider list
```
##### <a name="ParametersAttestationProvidersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="AttestationProvidersGet">Command `az attestation attestation-provider show`</a>

##### <a name="ExamplesAttestationProvidersGet">Example</a>
```
az attestation attestation-provider show --provider-name "myattestationprovider" --resource-group "MyResourceGroup"
```
##### <a name="ParametersAttestationProvidersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Name of the attestation service instance|provider_name|providerName|

#### <a name="AttestationProvidersCreate">Command `az attestation attestation-provider create`</a>

##### <a name="ExamplesAttestationProvidersCreate">Example</a>
```
az attestation attestation-provider create --provider-name "myattestationprovider" --resource-group "MyResourceGroup"
```
##### <a name="ParametersAttestationProvidersCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Name of the attestation service instance.|provider_name|providerName|
|**--location**|string|The supported Azure location where the attestation service instance should be created.|location|location|
|**--tags**|dictionary|The tags that will be assigned to the attestation service instance.|tags|tags|
|**--policy-signing-certificates-keys**|array|The value of the "keys" parameter is an array of JWK values.  By default, the order of the JWK values within the array does not imply an order of preference among them, although applications of JWK Sets can choose to assign a meaning to the order for their purposes, if desired.|keys|keys|

#### <a name="AttestationProvidersUpdate">Command `az attestation attestation-provider update`</a>

##### <a name="ExamplesAttestationProvidersUpdate">Example</a>
```
az attestation attestation-provider update --provider-name "myattestationprovider" --resource-group "MyResourceGroup" \
--tags Property1="Value1" Property2="Value2" Property3="Value3"
```
##### <a name="ParametersAttestationProvidersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Name of the attestation service instance.|provider_name|providerName|
|**--tags**|dictionary|The tags that will be assigned to the attestation service instance.|tags|tags|

#### <a name="AttestationProvidersDelete">Command `az attestation attestation-provider delete`</a>

##### <a name="ExamplesAttestationProvidersDelete">Example</a>
```
az attestation attestation-provider delete --provider-name "myattestationprovider" --resource-group \
"sample-resource-group"
```
##### <a name="ParametersAttestationProvidersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Name of the attestation service|provider_name|providerName|

#### <a name="AttestationProvidersGetDefaultByLocation">Command `az attestation attestation-provider get-default-by-location`</a>

##### <a name="ExamplesAttestationProvidersGetDefaultByLocation">Example</a>
```
az attestation attestation-provider get-default-by-location --location "Central US"
```
##### <a name="ParametersAttestationProvidersGetDefaultByLocation">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the default provider.|location|location|

#### <a name="AttestationProvidersListDefault">Command `az attestation attestation-provider list-default`</a>

##### <a name="ExamplesAttestationProvidersListDefault">Example</a>
```
az attestation attestation-provider list-default
```
##### <a name="ParametersAttestationProvidersListDefault">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|