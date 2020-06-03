# Azure CLI Module Creation Report

### attestation attestation-provider create

create a attestation attestation-provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--provider-name**|string|Name of the attestation service|provider_name|
|**--location**|string|The supported Azure location where the attestation service instance should be created.|location|
|**--tags**|dictionary|The tags that will be assigned to the attestation service instance.|tags|
|**--attestation-policy**|string|Name of attestation policy.|attestation_policy|
|**--policy-signing-certificates-keys**|array|The value of the "keys" parameter is an array of JWK values.  By
default, the order of the JWK values within the array does not imply
an order of preference among them, although applications of JWK Sets
can choose to assign a meaning to the order for their purposes, if
desired.|keys|
### attestation attestation-provider delete

delete a attestation attestation-provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--provider-name**|string|Name of the attestation service|provider_name|
### attestation attestation-provider list

list a attestation attestation-provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### attestation attestation-provider show

show a attestation attestation-provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--provider-name**|string|Name of the attestation service instance|provider_name|