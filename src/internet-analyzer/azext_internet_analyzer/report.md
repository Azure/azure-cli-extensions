# Azure CLI Module Creation Report

## -

## internet-analyzer preconfigured-endpoint

### internet-analyzer preconfigured-endpoint list

list a internet-analyzer preconfigured-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
## internet-analyzer profile

### internet-analyzer profile create

create a internet-analyzer profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--etag|str|Gets a unique read-only string that changes whenever the resource is updated.|/etag|/etag|

**Example: Creates an NetworkExperiment Profile in a Resource Group**

```
internet-analyzer profile create --profile-name Profile1
        --name rg1
        --location WestUs
        --enabled-state Enabled
```
### internet-analyzer profile update

update a internet-analyzer profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--etag|str|Gets a unique read-only string that changes whenever the resource is updated.|/etag|/etag|

**Example: Updates an Experiment**

```
internet-analyzer profile update --profile-name Profile1
        --name rg1
        --enabled-state Enabled
```
### internet-analyzer profile delete

delete a internet-analyzer profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|

**Example: Deletes an NetworkExperiment Profile by ProfileName**

```
internet-analyzer profile delete --name rg1
        --profile-name Profile1
```
### internet-analyzer profile list

list a internet-analyzer profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
### internet-analyzer profile show

show a internet-analyzer profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
## internet-analyzer scorecard timeseries

## internet-analyzer test

### internet-analyzer test create

create a internet-analyzer test.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--description|str|The description of the details or intents of the Experiment|/description|/properties/description|
|--endpoint-a-name|str|The name of the endpoint|/endpoint_a/name|/properties/endpointA/name|
|--endpoint-a-endpoint|str|The endpoint URL|/endpoint_a/endpoint|/properties/endpointA/endpoint|
|--endpoint-b-name|str|The name of the endpoint|/endpoint_b/name|/properties/endpointB/name|
|--endpoint-b-endpoint|str|The endpoint URL|/endpoint_b/endpoint|/properties/endpointB/endpoint|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|

**Example: Creates an Experiment**

```
internet-analyzer test create --resource-group rg1
        --profile-name Profile1
        --name Experiment1
        --description "this is my first experiment!"
        --endpoint-a-name "endpoint A"
        --endpoint-a-endpoint endpointA.net
        --endpoint-b-name "endpoint B"
        --endpoint-b-endpoint endpointB.net
        --enabled-state Enabled
```
### internet-analyzer test update

update a internet-analyzer test.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--description|str|The description of the details or intents of the Experiment|/description|/properties/description|
|--endpoint-a-name|str|The name of the endpoint|/endpoint_a/name|/properties/endpointA/name|
|--endpoint-a-endpoint|str|The endpoint URL|/endpoint_a/endpoint|/properties/endpointA/endpoint|
|--endpoint-b-name|str|The name of the endpoint|/endpoint_b/name|/properties/endpointB/name|
|--endpoint-b-endpoint|str|The endpoint URL|/endpoint_b/endpoint|/properties/endpointB/endpoint|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|

**Example: Updates an Experiment**

```
internet-analyzer test update --resource-group rg1
        --profile-name Profile1
        --name Experiment1
        --description string
        --enabled-state Enabled
```
### internet-analyzer test delete

delete a internet-analyzer test.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|

**Example: Deletes an Experiment**

```
internet-analyzer test delete --resource-group rg1
        --profile-name Profile1
        --name Experiment1
```
### internet-analyzer test list

list a internet-analyzer test.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
### internet-analyzer test show

show a internet-analyzer test.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|